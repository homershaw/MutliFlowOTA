# MutliFlowOTA

Public firmware artifact repository for MultiFlow and RIOT controllers.

This public repository contains **firmware binaries, packaged Introduction
demos, reusable device profiles and operator setup documentation only**.
Firmware and demo development source remains in the source repositories.

## Controller-specific releases

Never install an image based only on its filename or MCU family. JC and Nano
both use ESP32-P4 but have different hardware mappings and build targets.

| Directory | Manifest platform | Status |
|---|---|---|
| [JC-Riot](JC-Riot/) | `JC-ESP32P4-M3-DEV` | Tested application image; JC OTA integration pending |
| [P4-NANO](P4-NANO/) | `ESP32-P4-NANO` | Tested application image; Nano OTA integration pending |
| [P4-TRMNL](P4-TRMNL/) | `TRMNL_XIAO_EPAPER` | Existing RIOT-Flow TRMNL release, moved without changing its binary |

`P4-TRMNL` is the operator-selected name for the existing RIOT-Flow TRMNL
release. Directory naming does not change the image's hardware compatibility.
The old `riot-flow` directory contains only a compatibility manifest pointing
to `P4-TRMNL/firmware.bin`, so installed checkers keep their existing manifest
URL without maintaining a second binary.

Each published JC/Nano directory contains `manifest.json` and an application-only
`firmware.bin`. Its manifest records the exact embedded build identity, byte
count, SHA-256, source checkpoint and tested hardware. Images were built before
the source checkpoint commits, so their embedded identities retain `+dirty`;
they have not been relabelled or rebuilt after hardware testing.

These application images are **not** factory/full-flash images and contain no
bootloader, partition table, filesystem, SD data or saved controller settings.
Retain the controller's compatible bootloader and configuration. Do not write
these images at flash offset zero or use them to commission a bare board.

Publishing an artifact does not enable an updater on installed controllers.
Current JC/Nano releases do not yet include the firmware checker/browser
installer. Their safe serial installation was tested; OTA slot switching,
failure/recovery and controller-side platform rejection still require validation
when the updater is ported. A SHA-256 checks integrity, not publisher authenticity.
Future updaters must check platform metadata and the actual image's compatibility,
not trust a supplied filename or browser-only check.

No configuration backup, credentials, private runtime snapshots or source trees
belong in this public repository.

## Introduction demos (Windows x64)

Each controller directory has its own `riot_controller_introduction.zip`:

- [JC-Riot demo](JC-Riot/riot_controller_introduction.zip)
- [P4-NANO demo](P4-NANO/riot_controller_introduction.zip)
- [P4-TRMNL demo](P4-TRMNL/riot_controller_introduction.zip)

Extract the whole ZIP and double-click `RIOT-Introduction.exe`. Python is bundled;
no Python installation, build tools or controller hardware is required. Keep the
console open and use the printed `http://127.0.0.1:8080` address if the default
browser does not open. Close the console or press Ctrl+C to stop. For another
port, run `.\RIOT-Introduction.exe --port 8081` from PowerShell.

These are **separate packages of the same shared JC-Riot first-start
walkthrough**, not board-specific hardware simulators. The Communications panel
is a read-only JC illustration, including in the Nano and P4-TRMNL packages.
The demo does not qualify or alter the existing TRMNL firmware release.
The optional Tag Prototype is an illustrative design, not implemented firmware.

All values/actions are simulated locally. There is no field-device connection,
TOML validation, firmware installation or real Email sending. Each package uses
its own saved demo state under `%LOCALAPPDATA%\RIOT\Introduction\<controller>`.
No saved sessions ship in the ZIPs. Use Reset Demo for a blank walkthrough;
prototype settings remain separate. The executable is unsigned; inspect your
organization's download policy rather than disabling Windows security controls.
Packaging is not encryption or a guarantee against reverse engineering.

Only the runnable executable, package identity and operator/license documents
ship in each ZIP; no Python source, tests, development scripts or real controller
configuration is included. The older root-level source-containing Introduction
ZIP has been removed from the current tree. Git history is not rewritten.
Download hashes are listed in [INTRODUCTION-SHA256SUMS.txt](INTRODUCTION-SHA256SUMS.txt).

Publication checks: 31 existing demo/prototype tests passed. Each ZIP was
extracted and its executable checked without Python on PATH for blank start,
the 12-point M31 walkthrough, Save/CSV, restart persistence, isolated state,
port conflicts and invalid-state retention. The packaged JC copy was also
opened in a browser for Add M31 and Tag selection/Save; its Tags page had no
document overflow at measured 320/1440 CSS-pixel widths. These are Windows
desktop simulation checks, not controller hardware qualification. Automatic
default-browser opening and SmartScreen behavior are environment-dependent;
manual loopback browser access was checked.

## Shared devices

[toml/](toml/) is the common device-profile library for all controller families.
It currently contains publication/installation guidance only, not unreviewed
profiles or site configuration.

## Existing legacy files (unchanged)

- `manifest.json` — update metadata read by the controller
- `firmware.bin` — compiled PlatformIO firmware image for the DIS0705H target

## Release management

For JC/Nano, publish a verified application image and its board-specific manifest
in the same commit. Verify the exact embedded build identity, platform marker,
ESP chip/image format, size and SHA-256 before publishing. Record the source
checkpoint and runtime evidence honestly; never promote a build-only result to
hardware-tested or OTA-tested. Never move or overwrite another family's release
to make room for a new one. The TRMNL move preserves its existing release
metadata and binary; it is not a new build or a new hardware/OTA qualification.

### Legacy MultiFlow development release process

1. Build the private MultiFlow project with PlatformIO.
2. Copy:
   `.pio/build/dis0705h_standalone/firmware.bin`
   into this repository as `firmware.bin`.
3. Calculate the SHA-256 of `firmware.bin`.
4. Update `manifest.json` with:
   - `version`
   - `firmware_url`
   - `sha256`
   - `size`
   - `notes`
5. Commit both files together.
6. Test on the dedicated OTA test controller before promoting a build.

## Production

This public GitHub location is for development only. The controller updater is designed so the manifest URL can later be changed to a secure production update website.
