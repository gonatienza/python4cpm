# Changelog

Python4CPM Changelog

## [Unreleased]

## [1.1.3.2] - 2026-03-13

### Added
- `EnvHandler` enhancements in .NET.

## [1.1.3.1] - 2026-03-12

### Added
- `RequiresNewPassword` abstract property in .NET.

## [1.1.3] - 2026-03-11

### Changed
- Properties from `python4cpm.accounts.TargetAccount`, `python4cpm.accounts.LogonAccount`, `python4cpm.accounts.ReconcileAccount` and `python4cpm.args.Args` return `None` if not set instead of and empty string.
- If all properties of either `python4cpm.accounts.TargetAccount`, `python4cpm.accounts.LogonAccount` or `python4cpm.accounts.ReconcileAccount` return None, the object itself returns None.

## [1.1.2.1] - 2026-03-08

### Added
- `EnvHandler` to .NET.

## [1.1.2] - 2026-03-08

### Added
- `python4cpm.envhandler.EnvHandler` as the environment context handler base modeling class.
- `python4cpm.accounts.TargetAccount`, `python4cpm.accounts.LogonAccount` and `python4cpm.accounts.ReconcileAccount` objects to contain all account data in python module.
- Zeroing of plaintext buffers in python.

### Changed
- Moved some `python4cpm.args.Args` properties to the newly added account objects.
- Moved all `python4cpm.secrets.Secrets` properties to the newly added account objects.

### Removed
- `python4cpm.secrets.Secrets` object.

## [1.0.27] - 2026-03-03

### Added
- `EncryptedString` object to contain encrypted blobs in .NET.
- Verbosity in debug logs for .NET.

## [1.0.26] - 2026-03-02

### Added
- Support for SRS.
- `Python4CPMHandler` abstract class.
- Optional "Port" property for platform.

### Changed
- `Python4CPM` logger default directory, file naming convention and formatting.
- `NETHelper` initialization replaced with `NETHelper.set()` and `NETHelper.get()`.

## [1.0.20] - 2026-02-26

### Changed
- If `close_success()` or `close_fail()` are not used to end the python script that initiated a `python4cpm.Python4CPM` object, the default behavior was modified to `close_fail(unrecoverable=True)` with an error message into the logs.

## [1.0.19] - 2026-02-24

### Changed
- Modified Python4CPM class and plugin platform to work with the [Credential Management .NET SDK](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-netinvoker.htm).

### Added
- Secured handoff of secrets between the Credential Management .NET SDK and Python to be protected by [DPAPI](https://learn.microsoft.com/en-us/dotnet/standard/security/how-to-use-data-protection).
    - DPAPI encryption through `ProtectedData.Protect`, keeping memory hygiene in .NET to clear any plaintext secrets used for the encryption.
    - Passes encrypted blobs through base64 encoding for the Python subprocess execution.
    - During the object `python4cpm.Python4CPM` initialization in Python, secrets are now kept in the `python4cpm.Secret` object encrypted at all times.
    - The secret plaintext `str` object is only created when calling the `python4cpm.Secret` object `get()` method.

### Removed
- `python4cpm.TPCHelper` which was replaced by `python4cpm.NETHelper`.

## [1.0.14] - 2026-02-17

### Added
- Added Python4CPM class and plugin platform to work with [CyberArk Terminal Plugin Controller](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-terminal-plugin-controller.htm).

[Unreleased]: https://github.com/gonatienza/python4cpm/compare/e33b863...HEAD
[1.1.3.2]: https://github.com/gonatienza/python4cpm/compare/f127687...e33b863
[1.1.3.1]: https://github.com/gonatienza/python4cpm/compare/v1.1.3...f127687
[1.1.3]: https://github.com/gonatienza/python4cpm/compare/2935b9e...v1.1.3
[1.1.2.1]: https://github.com/gonatienza/python4cpm/compare/v1.1.2...2935b9e
[1.1.2]: https://github.com/gonatienza/python4cpm/compare/v1.0.27...v1.1.2
[1.0.27]: https://github.com/gonatienza/python4cpm/compare/v1.0.26...v1.0.27
[1.0.26]: https://github.com/gonatienza/python4cpm/compare/v1.0.20...v1.0.26
[1.0.20]: https://github.com/gonatienza/python4cpm/compare/v1.0.19...v1.0.20
[1.0.19]: https://github.com/gonatienza/python4cpm/compare/v1.0.14...v1.0.19
[1.0.14]: https://github.com/gonatienza/python4cpm/compare/72ca757...v1.0.14
