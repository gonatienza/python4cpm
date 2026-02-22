# Changelog

Python4CPM Changelog

## [Unreleased]

## [1.0.16] - 2026-02-22

### Changed
- Modified Python4cpm module and plugin platform to work with the [Credential Management .NET SDK](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-netinvoker.htm).

### Added
- Secured handoff of secrets between the Credential Management .NET SDK and Python to be protected by [DPAPI](https://learn.microsoft.com/en-us/dotnet/standard/security/how-to-use-data-protection).
    - Added DPAPI Encryption through `ProtectedData.Protect`.
    - Added memory hygiene in the .NET handoff to clear the presence of plaintext secrets in managed/unmanaged memory.
    - Added transfer of encrypted blobs through base64 encoding in environment variables for the Python subprocess execution.
    - During the object `python4cpm.Python4CPM` initialization in Python, secrets are now kept in the `python4cpm.Secret` object encrypted at all times.
    - The secret plaintext `str` object is only created when calling the `python4cpm.Secret` object `get()` method.

## [1.0.14] - 2026-02-17

### Added
- Added Python4CPM module and plugin platform to work with [CyberArk Terminal Plugin Controller](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-terminal-plugin-controller.htm).

[Unreleased]: https://github.com/gonatienza/python4cpm/compare/v1.0.16...HEAD
[1.0.16]: https://github.com/gonatienza/python4cpm/compare/v1.0.14...v1.0.16
[1.0.14]: https://github.com/gonatienza/python4cpm/releases/tag/v1.0.14
