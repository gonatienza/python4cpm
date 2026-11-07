# Python4CPM

A simple and secure way of using python scripts with Idira/CyberArk CPM/SRS password rotations.

## How it works

This module leverages the [Credential Management .NET SDK](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-netinvoker.htm) from CyberArk to securely offload a password rotation logic into Python.

All objects are collected from the SDK and sent as environment context to be picked up by the `python4cpm` module during the subprocess execution of python. All secrets of such environment are protected and encrypted by [Data Protection API (DPAPI)](https://learn.microsoft.com/en-us/dotnet/standard/security/how-to-use-data-protection), until they are explicitely retrieved in your python script runtime, invoking the `Secret.get()` method.  Finally, python controls the termination signal sent back to the SDK, which is consequently used as the return code to CPM/SRS.  Such as a successful or failed (recoverable or not) result of the requested action.

This platform allows you to duplicate it multiple times, simply changing its settings (from Privilege Cloud/PVWA) to point to different venvs and/or python scripts.

## Installation

### Preparing Python

1. Install Python 3.11 or later along CPM or the SRS Connector Management Agent.
    - **Python must be installed for all users**.  Follow the custom install steps from the installation wizard to check the checkbox.
2. Create a venv in the server, by running `py -m venv c:\venv`.  If desired, use a custom location and adjust any future references.
3. Install `python4cpm` in your venv:
    - If your CPM/SRS can connect to the internet, install with `c:\venv\Scripts\pip.exe install python4cpm`.
    - If your CPM/SRS cannot connect to the internet:
        - Download the latest `python4cpm-*.whl` file from the [pypi project files](https://pypi.org/project/python4cpm/#files).
        - Copy the file to the server into a temporary directory called `python4cpm-wheel`.
        - From the parent directory of `python4cpm-wheel` run `c:\venv\Scripts\pip.exe install --no-index --find-links=.\python4cpm-wheel python4cpm`.


### Importing the platform

#### If you are using CPM (SaaS or Self-Hosted):
1. Download the latest [Credential Management .NET SDK](https://community.cyberark.com/marketplace/s/#a3550000000EkA0AAK-a3950000000jjoOAAQ) and place its content in the bin folder of CPM (`C:\Program Files (x86)\CyberArk\Password Manager\bin`).  The files for this may already be present.
2. Download the `python4cpm-platform-*.zip` asset from the latest  [release](https://github.com/gonatienza/python4cpm/releases).
3. Import the platform zip file into Privilege Cloud/PVWA `(Administration -> Platform Management -> Import platform)`.
4. Craft your python script and place it within a folder in CPM (e.g., `C:\python4cpm-scripts`).
5. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
6. Edit the duplicated platform and specify the path of your script, under `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonScriptPath -> Value` (e.g., `C:\python4cpm-scripts\myapp.py`).
7. Also update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonExePath -> Value` with the custom path for the venv's `python.exe` file (e.g., `c:\venv\Scripts\python.exe`).
8. If you want to change the logging level, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLoggingLevel -> Value` to `critical`, `error`, `warning`, `info` or `debug`.
9. For new applications repeat steps from 4 to 8.

#### If you are using SRS (SaaS only):
1. Download the `python4cpm-platform-*.zip` asset from the latest  [release](https://github.com/gonatienza/python4cpm/releases).
2. Import the platform zip file into Privilege Cloud `(Administration -> Platform Management -> Import platform)`.
3. Craft your python script and place it within a folder in the Cloud Connector (where the SRS Management Agent runs) (e.g., `C:\python4cpm-scripts`).
4. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
5. Edit the duplicated platform and specify the path of your script, under `Plugin Settings -> Additional Parameters -> PythonScriptPath` (e.g., `C:\python4cpm-scripts\myapp.py`).
6. Also update `Plugin Settings -> Additional Parameters -> PythonExePath` with the custom path for the venv's `python.exe` file (e.g., `c:\venv\Scripts\python.exe`).
7. If you want to change the logging level, update `Plugin Settings -> Additional Parameters -> PythonLoggingLevel -> Value` to `critical`, `error`, `warning`, `info` or `debug`.
8. For new applications repeat steps from 3 to 7.

### Platform defaults

**Automatic verification and change are enabled by default.**  Only assign accounts to a duplicated platform that has `PythonExePath` and `PythonScriptPath` set.  The imported platform ships with the placeholder `ReplaceWithAbsolutePath`, which fails with `8900` without starting Python.  Adjust these defaults to match your application:

| Setting | Default | Meaning |
| --- | --- | --- |
| `PerformPeriodicChange` | `Yes` | Rotate automatically |
| `ExpirationPeriod` | `90` | Days before a password expires |
| `VFPerformPeriodicVerification` | `Yes` | Verify automatically |
| `Interval` | `1440` | Minutes |
| `Timeout` | `120` | Seconds |
| `MaximumRetries` | `5` | Retries |
| `MinDelayBetweenRetries` | `90` | Minutes between retries |
| `UnrecoverableErrors` | `8900` | Return codes treated as unrecoverable |
| `RCAutomaticReconcileWhenUnsynched` | `Yes` | Reconcile when unsynched |
| `PasswordLength`, `MinUpperCase`, `MinLowerCase`, `MinDigit`, `MinSpecial` | `12`, `2`, `2`, `1`, `1` | Rules for generating `new_password` |
| `PasswordForbiddenChars` | Empty | Characters the new password must not contain |

The new password is generated for you, so **make the password rules match the target system's policy**.  Your script only applies it.

Accounts require `Username` and `Address`, and `Port` is optional.  Link a `LogonAccount` and a `ReconcileAccount` if your script needs them.

## Python Script

```python
from python4cpm import Python4CPMHandler


class CredManager(Python4CPMHandler):
    """
    Properties:
        target_account (TargetAccount): Account being managed.
            .username (str): Account username.
            .address (str): Target address.
            .port (str | None): Target port.
            .policy_id (str): Platform ID.
            .safe_name (str): Safe name.
            .object_name (str): Account name in the vault.
            .password (Secret | None): Current password. Call .get() to retrieve value as many times as needed.
            .new_password (Secret | None): Replacement password. Call .get() to retrieve value as many times as needed.

        logon_account (LogonAccount | None): Linked Logon Account.
            .username (str): Account username.
            .password (Secret | None): Logon password. Call .get() to retrieve value.

        reconcile_account (ReconcileAccount | None): Linked Reconcile Account.
            .username (str): Account username.
            .password (Secret | None): Reconcile password. Call .get() to retrieve value.

        args (Args): Execution arguments.
            .action (str): Requested action.
            .logging_level (str | None): Value of PythonLoggingLevel.

        logger (logging.Logger): Logger instance.

    Methods:
        close_success(): Signal successful completion and terminate.
        close_fail(): Signal failed completion and terminate.
    """


    def verify(self):
        """
        REQUIRED METHOD
        """
        # TODO: use account objects for your logic
        self.close_success()

    def logon(self):
        """
        REQUIRED METHOD
        """
        # TODO: use account objects for your logic
        self.close_success()

    def change(self):
        """
        REQUIRED METHOD
        """
        # TODO: use account objects for your logic
        self.close_success()

    def prereconcile(self):
        """
        REQUIRED METHOD
        """
        # TODO: use account objects for your logic
        self.close_success()

    def reconcile(self):
        """
        REQUIRED METHOD
        """
        # TODO: use account objects for your logic
        self.close_success()


if __name__ == "__main__":
    CredManager().run() # initializes the class and calls the action that was requested from CPM/SRS.
```
(*) More realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify -> the script will be executed once running the `verify()` method.
2. Change -> the script will be executed twice: first `logon()`, then `change()`.
3. Reconcile -> the script will be executed twice: first `prereconcile()`, then `reconcile()`.
4. When calling `verify()`, `logon()` or `prereconcile()`: `target_account.new_password` will always return `None`.
5. If a logon account is not linked, `logon_account` will return `None`.
6. If a reconcile account is not linked, `reconcile_account` will return `None`.
7. **Always** use the `close_success` or `close_fail` methods to signal the proper termination for all actions.
    - `close_fail` takes the optional argument of `unrecoverable` as a bool flag (by default set to `False`).  It signals CPM whether the error you encountered cannot be solved through the rotation logic or requires manual intervention.  E.g., a regular rotation fails (which is still recoverable) and when called for a reconciliation process it fails too (at this point the error encountered is not recoverable).
    - If any action is not terminated with a termination method, CPM/SRS will see this as a `close_fail(unrecoverable=True)`.  This happens regardless of whether it was terminated by an exception or no exception was raised.  **If you rotate a credential successfully and do not close with success, you will have a rotated credential that will be lost and not saved into the vault**.
8. The python `Logger` places its logs in the `Logs/ThirdParty` directory.

### Writing a rotation script

#### What each method should do

| Method | Action | `new_password` | What to do |
| --- | --- | --- | --- |
| `verify()` | `verifypass` | `None` | Authenticate with `target_account`. |
| `logon()` | `logon` | `None` | Prepare for `change()`.  It can just call `close_success()`. |
| `change()` | `changepass` | Set | Authenticate, then set `target_account.new_password` on the target. |
| `prereconcile()` | `prereconcilepass` | `None` | Authenticate with `reconcile_account`. |
| `reconcile()` | `reconcilepass` | Set | Authenticate with `reconcile_account`, then set `target_account.new_password` on `target_account.username`. |

Use `reconcile_account` for `prereconcile()` and `reconcile()`, because `target_account.password` is not expected to work when reconciling.

#### Return codes

| Script result | Python exit code | Returned to CPM/SRS |
| --- | --- | --- |
| `close_success()` | `10` | `0` (success) |
| `close_fail()` | `81` | `8100` (recoverable) |
| `close_fail(unrecoverable=True)` | `89` | `8900` (unrecoverable) |
| Unhandled exception | `1` | `8900` (unrecoverable) |
| No close method called | `0` | `8900` (unrecoverable) |
| Any other exit code | That code | `8900` (unrecoverable) |
| `PythonExePath` or `PythonScriptPath` not found | Python is not started | `8900` (unrecoverable) |

#### Rules for your script

- **Every method runs in a new python process.**  Nothing in memory is shared between `logon()` and `change()`, or between `prereconcile()` and `reconcile()`.
- **Implement all five methods.**  A missing method raises a `TypeError` when the class is created, which returns `8900`.
- **If you override `__init__`, call `super().__init__()` first.**
- **Check for `None`.**  Empty values are not sent, so these can all be `None`: `port`, any `password`, and `new_password`.  A linked account can have a username and no password.  `.get()` on `None` raises an `AttributeError`.
- **`address` is the raw value from the account.**  Build URLs yourself, and pick a default for when `port` is `None`.
- **Change the password last.**  Close with `close_success()` straight after the target accepts it, and do nothing that can fail in between.
- **Close methods raise `SystemExit`.**  They are safe inside `try/except Exception`, and code after them does not run, except `finally` blocks.  A bare `except:` or `except BaseException:` catches them, and that action then returns `8900`.
- **Set a timeout on every network call.**  The plugin waits for python with no time limit of its own, so keep each action under the platform's `Timeout`.
- **Use `self.logger`, not `print`.**  Standard output is not captured.  Standard error is written to the plugin log when an action fails.
- **Never log the result of `.get()`.**  Logging a `Secret` itself is safe and shows `[ENCRYPTED]`.  Keep secrets out of exception messages too, as tracebacks reach the plugin log.
- **Use absolute paths.**  The working directory is inherited from the CPM/SRS process, not taken from your script's folder.
- **Keep TLS verification on in production.**  The `simpleauthcredmanager.py` example turns it off.

Common failures can be handled like this:

```python
def verify(self):
    try:
        self._login(self.target_account)
    except Exception as e:
        self.logger.error(f"{type(e).__name__}: {e}")
        self.close_fail()
    self.close_success()
```

Use `close_fail()` for what a later attempt could fix, like a timeout or a rejected password.  Use `close_fail(unrecoverable=True)` for what needs manual intervention.

#### Logs

All logs are in `Logs/ThirdParty`, relative to the working directory.

| File | Content |
| --- | --- |
| `python4cpm.loggerhandler_<level>_<PolicyID>-<SafeName>-<ObjectName>.log` | `self.logger` output.  Rotates at 1 MB and keeps one backup. |
| `<PolicyID>-<SafeName>-<FolderName>-<ObjectName>.Log` | The last error, with its error code. |
| `Debug_<PolicyID>-<SafeName>-<FolderName>-<ObjectName>_CANetPluginInvoker_<date>.log` | Plugin trace, written with `Debug=Yes` in a manual run, including paths, values and standard error. |

The default level is `error`, so `self.logger.info()` and `self.logger.debug()` write nothing until you change `PythonLoggingLevel`.  An unknown level falls back to `error`, and `critical` is the quietest.  Logging cannot be turned off.

#### Troubleshooting

| Log message | Cause |
| --- | --- |
| `PythonExePath: '...' not found` or `PythonScriptPath: '...' not found` | Wrong path, or the account is still on the imported platform. |
| `Python closed with exit code: 0` and `No close signal called` | A method ended without a close method. |
| `Python closed with exit code: 1` | Unhandled exception.  The traceback follows in `StdErr Output`. |
| `Python closed with failed recoverable` | The script called `close_fail()`. |
| `Python closed with failed unrecoverable` | The script called `close_fail(unrecoverable=True)`. |
| `can't open file '...\ C:\...'` | A manual `.ini` file has spaces around `=`. |


### Installing dependencies in python venv

As with any python venv, you can install dependencies in your venv.
1. If your CPM can connect to the internet:
   - You can use regular pip install commands (e.g., `c:\venv\Scripts\pip.exe install requests`).
2. If your CPM cannot connect to the internet:
   - You can download packages for an offline install.  More info [here](https://pip.pypa.io/en/stable/cli/pip_download/).


## Dev Helper:

For dev purposes, `DevHelper` is a companion helper to test your scripts without CPM/SRS.  It simplifies the instantiation of the `Python4CPM` or `Python4CPMHandler` objects by simulating how the plugin creates the environment context for the python module.

**Note**: As CPM and the SRS management agent run in Windows, the plugin was built to encrypt secrets using DPAPI (a windows only library).  For dev purposes in Linux/Mac dev workstations, those secrets put in the environment context by `DevHelper` will be in plaintext.  In windows dev workstations, `DevHelper` encrypts the secrets as the .NET plugin does.  This is informational only, **the module will use its encryption/decryption capabilities automatically based on the platform** it is running on and you do not have to do anything specific to enable it.

### Example:

#### Set your arguments and secrets:

```python
from python4cpm import DevHelper, Python4CPM, Python4CPMHandler

DevHelper.set(
    action=Python4CPM.ACTION_CHANGE, # use actions from Python4CPM.ACTION_*
    logging_level="debug",
    target_policy_id="DevHelper", # name of platform
    target_safe_name="Safename", # name of safe
    target_object_name="Objectname", # name of account
    target_username="jdoe",
    target_address="myapp.corp.local",
    target_port="8443",
    logon_username="ldoe",
    reconcile_username="rdoe",
    target_password="", # str value of target password (required by most scripts)
    logon_password="", # str value of logon password (leave out if not linked)
    reconcile_password="", # str value of reconcile password (leave out if not linked)
    target_new_password="" # str value of new password (only for change and reconcile)
)

class CredManager(Python4CPMHandler):
    def verify(self):
        # TODO: Add your logic here
        self.close_success()

    def logon(self):
        # TODO: Add your logic here
        self.close_success()

    def change(self):
        # TODO: Add your logic here
        self.close_success()

    def prereconcile(self):
        # TODO: Add your logic here
        self.close_success()

    def reconcile(self):
        # TODO: Add your logic here
        self.close_success()

CredManager().run()
```

#### Remember when using `DevHelper`:

- `target_policy_id`, `target_safe_name` and `target_object_name` are required.  The log file name is built from them.
- A password left out or set to `""` becomes `None`, as in production.  Leave out `target_new_password` when testing `verify()`, `logon()` or `prereconcile()`.
- Each `DevHelper.set()` call replaces the previous one, so anything left out is cleared.
- Each run tests one `action`, so set it to test each of the five methods.
- Exit code `10` means success, and `81` or `89` mean the script called `close_fail()`.  Anything else returns `8900` in production.
- **Your script runs for real.**  `change()` and `reconcile()` change the password on the target, so use a test account.

#### Remember for your final script:

- Remove the import of `DevHelper`.
- Remove the `DevHelper.set()` call.
