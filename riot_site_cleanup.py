#!/usr/bin/env python3
"""Remove unused Site devices (and their Site Signal Tags) from a RIOT controller.

Dry run by default. With --apply it first downloads a full configuration
backup, then disables enabled Site routes that only feed removed devices and
removes each unused Site device through /api/site/config. Afterwards it checks
that every Tag that was in use (Dashboard, Rules, Flow, MQTT, History, Alarms)
is still present.

A Site device is kept if any of its Tags is used, if an enabled calculation
reads one of its signals or routes, or if another Tag's source mentions one of
its signals. Library devices, M31, MVS, Flow and controller Tags are never
touched.

Usage:
  python riot_site_cleanup.py 192.168.1.224              # report only
  python riot_site_cleanup.py 192.168.1.224 --apply      # back up, then remove
  python riot_site_cleanup.py HOST --keep "Radio" --apply
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TIMEOUT = 60


class Controller:
    def __init__(self, host):
        self.base = host if host.startswith("http") else "http://" + host
        self.base = self.base.rstrip("/")

    def request(self, path, method="GET", query=None):
        url = self.base + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = b"" if method == "POST" else None
        req = urllib.request.Request(url, data=data, method=method)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (urllib.error.URLError, OSError) as e:
            raise SystemExit(f"Cannot reach {self.base}{path}: {getattr(e, 'reason', e)}. No changes were made by this request.")

    def json(self, path, method="GET", query=None):
        status, body = self.request(path, method, query)
        try:
            payload = json.loads(body.decode("utf-8"))
        except ValueError:
            payload = {"ok": False, "error": body[:200].decode("utf-8", "replace")}
        return status, payload

    def catalog(self):
        rows, offset = [], 0
        while True:
            status, page = self.json("/api/tag-catalog", query={"offset": offset})
            if status != 200 or not page.get("ok"):
                raise SystemExit(f"Tag catalog unavailable: {status} {page.get('error')}")
            rows += page.get("rows", [])
            nxt = page.get("next")
            if not nxt or len(rows) >= page.get("total", 0):
                return rows
            offset = nxt

    def site(self):
        status, site = self.json("/api/site")
        if status != 200 or not site.get("ok"):
            raise SystemExit(f"Site configuration unavailable: {status} {site.get('error')}")
        if not site.get("configValid", True):
            raise SystemExit("Site configuration is not valid on the controller; stopping.")
        return site


def used(row):
    dash = row.get("dashboardParticipation") or {}
    return bool(row.get("rules") or row.get("flow") or row.get("mqtt") or row.get("mqttSelected")
                or row.get("history") or row.get("alarm") or dash.get("visible")
                or dash.get("placements"))


def used_refs(rows):
    return sorted(r["ref"] for r in rows if used(r))


def plan(site, rows, keep_names):
    devices = {d["index"]: d for d in site["devices"] if d.get("present")}
    signals = [s for s in site["signals"] if s.get("present")]
    by_device = {}
    for s in signals:
        by_device.setdefault(s["device"], []).append(s)
    route_device = {}
    for r in site["routes"]:
        if r.get("source") == 0 and 0 <= r.get("signal", -1) < len(site["signals"]):
            sig = site["signals"][r["signal"]]
            if sig.get("present"):
                route_device[r["index"]] = sig["device"]

    remove, keep = [], []
    for i, d in sorted(devices.items()):
        tag = f"SITE.DEVICE.{i}"
        names = {s["logical"] for s in by_device.get(i, [])} | {s["name"] for s in by_device.get(i, [])}
        names |= {r["id"] for r in site["routes"] if route_device.get(r["index"]) == i}
        names.discard("")
        own = [r for r in rows if r.get("device") == tag]
        reasons = []
        if d["name"] in keep_names:
            reasons.append("kept by --keep")
        busy = [r["ref"] for r in own if used(r)]
        if busy:
            reasons.append("Tags in use: " + ", ".join(busy[:5]))
        calcs = [c["id"] for c in site["calculations"] if c.get("enabled") and c.get("input") in names]
        if calcs:
            reasons.append("read by enabled calculation " + ", ".join(calcs))
        refs = [r["ref"] for r in rows if r.get("device") != tag and r.get("kind", "").find("Site") < 0
                and any(n and n in (str(r.get("source", "")) + " " + str(r.get("related", ""))) for n in names)]
        if refs:
            reasons.append("referenced by " + ", ".join(refs[:5]))
        entry = {"index": i, "name": d["name"], "tags": len(own),
                 "routes": [r["index"] for r in site["routes"]
                            if r.get("enabled") and route_device.get(r["index"]) == i]}
        if reasons:
            entry["reasons"] = reasons
            keep.append(entry)
        else:
            remove.append(entry)
    return remove, keep


def backup(ctl, folder):
    folder.mkdir(parents=True, exist_ok=True)
    status, info = ctl.json("/api/backup/build", "POST", {"mode": "full"})
    if status != 200 or not info.get("validated"):
        raise SystemExit(f"Backup build failed: {status} {info.get('error')}")
    status, body = ctl.request("/api/backup/download")
    if status != 200 or len(body) != info.get("totalBytes"):
        raise SystemExit(f"Backup download failed or incomplete: {status} {len(body)} bytes")
    if not any(r.get("name") == "site" for r in info.get("records", [])):
        raise SystemExit("Backup does not contain the Site record; stopping.")
    (folder / "RiotP4_backup_full.riotbak").write_bytes(body)
    return info


def post_site(ctl, site_rev, query):
    for _ in range(20):
        q = dict(query, confirm="APPLY", revision=site_rev[0])
        status, body = ctl.json("/api/site/config", "POST", q)
        if status == 200 and body.get("ok", True):
            site_rev[0] = body["revision"]
            return
        if "Poll in progress" not in str(body.get("error")):
            raise SystemExit(f"Site change rejected ({query}): {status} {body.get('error')}")
        time.sleep(0.7)
    raise SystemExit(f"Controller stayed busy polling; stopped at {query}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("host", help="controller IP or URL, e.g. 192.168.1.224")
    ap.add_argument("--apply", action="store_true", help="back up, then remove the unused Site devices")
    ap.add_argument("--keep", action="append", default=[], help="Site device name to keep (repeatable)")
    ap.add_argument("--backup-dir", default=None, help="folder for the backup (default: ./riot-cleanup-<host>-<time>)")
    args = ap.parse_args()

    ctl = Controller(args.host)
    site, rows = ctl.site(), ctl.catalog()
    remove, keep = plan(site, rows, set(args.keep))
    print(f"Controller {ctl.base}: {len(rows)} Tags, {len(used_refs(rows))} in use, Site revision {site['revision']}")
    for e in keep:
        print(f"  KEEP   {e['name']} ({e['tags']} Tags): {'; '.join(e['reasons'])}")
    for e in remove:
        extra = f", disable routes {e['routes']}" if e["routes"] else ""
        print(f"  REMOVE {e['name']} ({e['tags']} Tags{extra})")
    if not remove:
        print("Nothing to remove.")
        return 0
    if not args.apply:
        print("Dry run only. Re-run with --apply to back up and remove.")
        return 0

    stamp = time.strftime("%Y%m%d-%H%M%S")
    folder = Path(args.backup_dir or f"riot-cleanup-{urllib.parse.urlparse(ctl.base).hostname}-{stamp}")
    info = backup(ctl, folder)
    (folder / "site_before.json").write_text(json.dumps(site, indent=1), encoding="utf-8")
    (folder / "tags_before.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"Backup saved: {folder.resolve()} ({info['totalBytes']} bytes, firmware {info.get('firmware')})")

    before = used_refs(rows)
    rev = [site["revision"]]
    for e in remove:
        for r in e["routes"]:
            post_site(ctl, rev, {"section": "route", "index": r, "enabled": 0})
            print(f"  route {r} disabled (revision {rev[0]})")
    for e in remove:
        post_site(ctl, rev, {"section": "device", "index": e["index"], "present": 0, "enabled": 0})
        print(f"  removed {e['name']} (revision {rev[0]})")

    after_rows = ctl.catalog()
    after = used_refs(after_rows)
    print(f"Tags: {len(rows)} -> {len(after_rows)}; in use {len(before)} -> {len(after)}")
    if before != after:
        print("WARNING: Tags in use changed: missing " + ", ".join(sorted(set(before) - set(after))))
        print("Restore the backup on the controller's Backup page if this was not intended.")
        return 2
    print("All Tags in use are unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
