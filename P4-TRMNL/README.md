# TRMNL controller release

`P4-TRMNL` is the operator-selected directory name for the existing RIOT-Flow
TRMNL release, formerly stored under `riot-flow`.

The existing `2.0.0-a7b2` application image is moved unchanged. Its manifest
retains product `Riot-Flow`, platform `TRMNL_XIAO_EPAPER`, version, hash, size,
channel and original release notes. A folder rename does not change the hardware
compatibility of an image. Do not install JC or Nano firmware on this target.

The image header identifies **ESP32-S3**, not ESP32-P4. The folder name is not a
chip identifier; preserve the `TRMNL_XIAO_EPAPER` compatibility check.

The `riot_controller_introduction.zip` in this directory is a Windows package of
the shared JC-Riot walkthrough, not TRMNL firmware or a TRMNL hardware simulator.
See its included setup guide for the simulation limits.

The old [riot-flow manifest](../riot-flow/manifest.json) remains solely for
installed checkers that already use that URL. It points to the firmware in this
directory. There is no duplicate binary in the old directory.
