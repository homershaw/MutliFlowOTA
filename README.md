# MutliFlowOTA

Public firmware artifact repository for MultiFlow and RIOT controllers.

This repository intentionally contains **only update artifacts**. The MultiFlow source repository remains private.

## Controller-specific releases

Never install an image based only on its filename or MCU family. JC and Nano
both use ESP32-P4 but have different hardware mappings and build targets.

| Directory | Manifest platform | Status |
|---|---|---|
| [JC-Riot](JC-Riot/) | `JC-ESP32P4-M3-DEV` | Tested application image; JC OTA integration pending |
| [P4-NANO](P4-NANO/) | `ESP32-P4-NANO` | Tested application image; Nano OTA integration pending |
| [P4-TRMNL](P4-TRMNL/) | Not assigned | Reserved; no approved P4-TRMNL image yet |
| [riot-flow](riot-flow/) | `TRMNL_XIAO_EPAPER` | Existing XIAO ePaper release; unchanged |

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

## Existing legacy files (unchanged)

- `manifest.json` — update metadata read by the controller
- `firmware.bin` — compiled PlatformIO firmware image for the DIS0705H target

## Release management

For JC/Nano, publish a verified application image and its board-specific manifest
in the same commit. Verify the exact embedded build identity, platform marker,
ESP chip/image format, size and SHA-256 before publishing. Record the source
checkpoint and runtime evidence honestly; never promote a build-only result to
hardware-tested or OTA-tested. Never move or overwrite another family's release
to make room for a new one. `P4-TRMNL` remains unavailable until its correct build
and hardware are identified and tested.

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
