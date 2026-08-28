# MutliFlowOTA

Public OTA artifact repository for the MultiFlow ESP32-S3 controller.

This repository intentionally contains **only update artifacts**. The MultiFlow source repository remains private.

## Files

- `manifest.json` — update metadata read by the controller
- `firmware.bin` — compiled PlatformIO firmware image for the DIS0705H target

## Development release process

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
