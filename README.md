# Python4CPM

A simple way of using python scripts with CyberArk CPM/SRS rotations.  This module leverages the [Credential Management .NET SDK](https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/pasimp/plug-in-netinvoker.htm) from CyberArk to securely offload a password rotation logic into a python script.

This platform allows you to duplicate it multiple times, simply changing its settings from Privilege Cloud/PVWA to point to different python scripts leveraging the module `python4cpm`.

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


class MyRotator(Python4CPMHandler): # create a subclass for the Handler
    """
    These are the usable properties and methods from Python4CPMHandler:

        self.args.action
        # action requested from CPM/SRS

        ## Target Account

        self.target_account.username
        # address from account

        self.target_account.address
        # address from account

        self.target_account.port
        # port from account

        self.target_account.password.get()
        # get plaintext str from password object

        ## Logon Account
        self.logon_account.username
        self.logon_account.password.get()

        ## Reconcile Account
        self.reconcile_account.username
        self.reconcile_account.password.get()

        ## Logging

        self.logger.critical("this is critical message")
        self.logger.error("this is an error message")
        self.logger.warning("this is a warning message")
        self.logger.info("this is an info message")
        self.logger.debug("this is a debug message")

        # logs are placed in Logs/ThirdParty/MyRotator.log

        ## The logging level comes from PythonLoggingLevel (platform parameters) (default is error)

    =============================
    REQUIRED TERMINATION SIGNALS
    =============================
    Terminate signals -> MUST use one of the following three signals to terminate the script:

        self.close_success()
        # terminate with success state

        self.close_fail()
        # terminate with recoverable failed state
        
        self.close_fail(unrecoverable=True)
        # terminate with unrecoverable failed state

    When calling a signal sys.exit is invoked and the script is terminated.
    If no signal is called, and the script finishes without any exception,
    it will behave like p4cpm.close_fail(unrecoverable=True) and log an error message.
    =============================
    =============================
    """

    # =============================
    # REQUIRED METHODS (MUST DEFINE)
    # =============================
    # verify(), logon(), change(), prereconcile(), reconcile()

    def verify(self):
        self._verify()
        self.log_info("verification successful")
        self.close_success()

    def logon(self):
        self.close_success()

    def change(self):
        self._change()
        self.log_error("something went wrong")
        self.close_fail()

    def prereconcile(self):
        self._verify(from_reconcile=True)
        self.close_success()

    def reconcile(self):
        self._change(from_reconcile=True)
        self.close_success()

    def _verify(self, from_reconcile=False):
        if from_reconcile is False:
            pass
            # TODO: use account objects for your logic
        else:
            pass
            # TODO: use account objects for your logic
        result = True
        if result is True:
            self.log_info("verification successful")
        else:
            self.log_error("something went wrong")
            self.close_fail()

    def _change(self, from_reconcile=False):
        if from_reconcile is False:
            pass
            # TODO: use account objects for your logic
        else:
            pass
            # TODO: use account objects for your logic
        result = True
        if result is True:
            self.log_info("rotation successful")
        else:
            self.log_error("something went wrong")
            self.close_fail()


if __name__ == "__main__":
    MyRotator().run() # initializes the class and calls the action that was requested from CPM/SRS.
```
(*) More realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify -> the sciprt will be executed once running the `MyRotator.verify()` method.
2. Change -> the sciprt will be executed twice, running first the `MyRotator.logon()` method and secondly the `MyRotator.change()` method.
    - If both actions are not terminated with `self.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `self.close_fail(unrecoverable=True)`.
3. Reconcile -> the sciprt will be executed twice, running first the `MyRotator.prereconcile()` method and secondly the `MyRotator.reconcile()` method.
    - If both actions are not terminated with `self.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `self.close_fail(unrecoverable=True)`.
4. When calling `MyRotator.verify()`, `MyRotator.logon()` or `MyRotator.prereconcile()`: `self.target_account.new_password.get()` will always return an empty string.
5. If a logon account is not linked, `self.logon_account.username` and `self.logon_account.password.get()` will return empty strings.
6. If a reconcile account is not linked, `self.reconcile_account.username` and `self.reconcile_account.password.get()` will return empty strings.


### Installing dependencies in python venv

As with any python venv, you can install dependencies in your venv.
1. If your CPM can connect to the internet:
   - You can use regular pip install commands (e.g., `c:\venv\Scripts\pip.exe install requests`).
2. If your CPM cannot connect to the internet:
   - You can download packages for an offline install.  More info [here](https://pip.pypa.io/en/stable/cli/pip_download/).


## Dev Helper:

For dev purposes, `NETHelper` is a companion helper that simplifies the instantiation of the `Python4CPM` or `Python4CPMHandler` objects by simulating how the plugin passes objects to the module.
Install this module (in a dev workstation) with:

```bash
pip install python4cpm
```

**Note**: As CPM runs in Windows, the plugin was built to pass secrets securely to the `Python4CPM.crypto` module using the Data Protection API (DPAPI).  For dev purposes in Linux/Mac dev workstations, those secrets will appear as plaintext in the environment of the process.  This is informational only, the module will use its encryption/decryption capabilities automatically in Windows and you do not have to do anything specific to enable it.

### Example:

#### Set your arguments and secrets:

```python
from python4cpm import NETHelper, Python4CPM, Python4CPMHandler
from getpass import getpass

# Get secrets for your password, logon account password, reconcile account password and new password
# You can use an empty string if it does not apply
target_password = getpass("password: ") # password from account
logon_password = getpass("logon_password: ") # password from linked logon account
reconcile_password = getpass("reconcile_password: ") # password from linked reconcile account
target_new_password = getpass("new_password: ") # new password for the rotation

NETHelper.set(
    action=Python4CPM.ACTION_CHANGE, # use actions from Python4CPM.ACTION_*
    target_username="jdoe",
    target_address="myapp.corp.local",
    target_port="8443",
    logon_username="ldoe",
    reconcile_username="rdoe",
    logging_level="debug", # "critical", "error", "warning", "info" or "debug"
    target_password=target_password,
    logon_password=logon_password,
    reconcile_password=reconcile_password,
    target_new_password=target_new_password
)

class MyRotator(Python4CPMHandler):
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

MyRotator().run()
```

#### Remember for your final script:

- Remove the import of `NETHelper`.
- Remove the `NETHelper.set()` call.
- If applicable, change the definition of `p4cpm` from `p4cpm = NETHelper.get()` to `p4cpm = Python4CPM("MyApp")`.
- Remove any secrets prompting or interactive interruptions.
