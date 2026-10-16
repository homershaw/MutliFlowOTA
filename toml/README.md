# Shared device profiles

This directory is the common home for public device `.toml` profiles used by
JC-Riot, P4-NANO and supported P4-TRMNL firmware. Do not duplicate the library
under each controller directory.

No device profiles have been published here yet. Existing private/local
profiles have not been reviewed for publication; an empty library must not be
interpreted as a validated device list.

## Installing a published profile

1. Select a profile matching the exact manufacturer, model and register-map
   revision of the field device.
2. Read its accompanying setup/validation notes and check firmware support.
   A shared file location does not guarantee identical driver or transport
   support across controller families.
3. Use the actual controller's Device Library TOML upload/import control, then
   create and configure the Device instance through its normal setup workflow.
4. Verify address, serial/transport settings, register offsets, byte/word order,
   units and scaling against the manufacturer documentation and bench readback
   before using values in alarms or controls. Keep output writes disabled until
   deliberately commissioned.

The Introduction demo does not import or validate real TOML files. Never upload
a simulator ZIP, controller firmware binary or configuration backup as a device
profile.

## Publication rules

Publish only reusable device definitions with operator setup notes. Include
manufacturer/model, profile revision, supported firmware/driver requirements,
units/addressing assumptions, and explicit simulated/bench/field validation
status. Do not include site settings, network addresses, credentials, saved
controller state, proprietary manuals or unapproved vendor material.
