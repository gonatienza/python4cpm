# Python4CPM

A simple and secure way of using python scripts with CyberArk CPM/SRS password rotations.

## How it works

This module leverages the [Credential Management .NET SDK](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-netinvoker.htm) from CyberArk to securely offload a password rotation logic into Python.

All objects are collected from the SDK and sent as environment context to be picked up by the `python4cpm` module during the subprocess execution of python. All secrets of such environment are protected and encrypted by [Data Protection API (DPAPI)](https://learn.microsoft.com/en-us/dotnet/standard/security/how-to-use-data-protection), until they are explicitely retrieved in your python script runtime, invoking the `Secret.get()` method.  Finally, python controls the termination signal sent back to the SDK, which is consequently used as the return code to CPM/SRS.  Such as a successful or failed (recoverable or not) result of the requested action.

This platform allows you to duplicate it multiple times, simply changing its settings (from Privilege Cloud/PVWA) to point to different venvs and/or python scripts.

## Installation

### Preparing Python

1. Install Python along CPM or the SRS Connector Management Agent.
    - **Python must be installed for all users**.  Follow the custom install steps from the installation wizard to check the checkbox.
3. Create a venv in the server, by running `py -m venv c:\venv`.  If desired, use a custom location and adjust any future references.
4. Install `python4cpm` in your venv:
    - If your CPM can connect to the internet, install with `c:\venv\Scripts\pip.exe install python4cpm`.
    - If your CPM cannot connect to the internet:
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
8. If you want to disable logging, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLogging -> Value` to `no`.
9. If you want to change the logging level to `debug`, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLoggingLevel -> Value` to `debug`.
10. For new applications repeat steps from 4 to 9.

#### If you are using SRS (SaaS only):
1. Download the `python4cpm-platform-*.zip` asset from the latest  [release](https://github.com/gonatienza/python4cpm/releases).
2. Import the platform zip file into Privilege Cloud `(Administration -> Platform Management -> Import platform)`.
3. Craft your python script and place it within a folder in the Cloud Connector (where the SRS Management Agent runs) (e.g., `C:\python4cpm-scripts`).
4. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
5. Edit the duplicated platform and specify the path of your script, under `Plugin Settings -> Additional Parameters -> PythonScriptPath` (e.g., `C:\python4cpm-scripts\myapp.py`).
6. Also update `Plugin Settings -> Additional Parameters -> PythonExePath` with the custom path for the venv's `python.exe` file (e.g., `c:\venv\Scripts\python.exe`).
7. If you want to disable logging, update `Plugin Settings -> Additional Parameters -> PythonLogging` to `no`.
8. If you want to change the logging level to `debug`, update `Plugin Settings -> Additional Parameters -> PythonLoggingLevel -> Value` to `debug`.
9. For new applications repeat steps from 3 to 8.

## Python Script

```python
from python4cpm import Python4CPMHandler


class CredManager(Python4CPMHandler):
    """
    Properties:
        target_account (TargetAccount): Account being managed.
            .policy_id (str): Platform name.
            .object_name (str): Account name.
            .username (str): Account username.
            .address (str): Target address.
            .port (str): Target port.
            .password (Secret): Current password. Call .get() to retrieve value.
            .new_password (Secret): Replacement password. Call .get() to retrieve value.

        logon_account (LogonAccount): Linked Logon Account.
            .username (str): Account username.
            .password (Secret): Logon password. Call .get() to retrieve value.

        reconcile_account (ReconcileAccount): Linked Reconcile Account.
            .username (str): Account username.
            .password (Secret): Reconcile password. Call .get() to retrieve value.

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
7. Always use the `close_success` or `close_fail` methods to signal the proper termination for all actions.
    - If any action is not terminated with a termination method, CPM/SRS will see this as a `close_fail(unrecoverable=True)`, even if no exceptions are raised.
8. The python `Logger` places its logs in the `Logs/ThirdParty` directory.  The filename will be based on `target_account.policy_id` and `target_account.object_name`.


### Installing dependencies in python venv

As with any python venv, you can install dependencies in your venv.
1. If your CPM can connect to the internet:
   - You can use regular pip install commands (e.g., `c:\venv\Scripts\pip.exe install requests`).
2. If your CPM cannot connect to the internet:
   - You can download packages for an offline install.  More info [here](https://pip.pypa.io/en/stable/cli/pip_download/).


## Dev Helper:

For dev purposes, `NETHelper` is a companion helper to test your scripts without CPM/SRS.  It simplifies the instantiation of the `Python4CPM` or `Python4CPMHandler` objects by simulating how the plugin creates the environment context for the python module.

**Note**: As CPM and the SRS management agent run in Windows, the plugin was built to encrypt secrets using DPAPI (a windows only library).  For dev purposes in Linux/Mac dev workstations, those secrets put in the environment context by `NETHelper` will be in plaintext.  In windows dev workstations, `NETHelper` encrypts the secrets as the .NET plugin does.  This is informational only, **the module will use its encryption/decryption capabilities automatically based on the platform** it is running on and you do not have to do anything specific to enable it.

### Example:

#### Set your arguments and secrets:

```python
from python4cpm import NETHelper, Python4CPM, Python4CPMHandler

NETHelper.set(
    action=Python4CPM.ACTION_CHANGE, # use actions from Python4CPM.ACTION_*
    logging_level="debug",
    target_policy_id="NETHelper",
    target_object_name="Objectname",
    target_username="jdoe",
    target_address="myapp.corp.local",
    target_port="8443",
    logon_username="ldoe",
    reconcile_username="rdoe",
    target_password="", # str value of target password 
    logon_password="", # str value of logon password
    reconcile_password="", # str value of reconcile password
    target_new_password="" # str value of new password
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

#### Remember for your final script:

- Remove the import of `NETHelper`.
- Remove the `NETHelper.set()` call.
