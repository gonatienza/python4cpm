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

### Using the handler (recommended):

```python
from python4cpm import Python4CPMHandler


class MyRotator(Python4CPMHandler): # create a subclass for the Handler
    """
    These are the usable properties and methods from Python4CPMHandler:
    
        self.args.action # action requested from CPM/SRS
        self.args.username # username from the account username field
        self.args.address # address from the account address field
        self.args.port # port from the account port field
        self.args.reconcile_username # reconcile username from the linked reconcile account
        self.args.logon_username # logon username from the linked logon account
        self.args.logging # used to carry the platform logging settings for python
        self.secrets.password.get() # get str from password received from the vault
        self.secrets.new_password.get() # get str from new password in case of a rotation
        self.secrets.logon_password.get() # get str from linked logon account password
        self.secrets.reconcile_password.get() # get str from linked reconcile account password

    Logging methods -> Will only log if PythonLogging (platform parameters) is set to yes (default is yes)
    
        self.log_error("this is an error message") # logs error into Logs/ThirdParty/MyRotator.log
        self.log_warning("this is a warning message") # logs warning into Logs/ThirdParty/MyRotator.log
        self.log_info("this is an info message") # logs info into Logs/ThirdParty/MyRotator.log
    
    Logging level -> Will only log debug messages if PythonLoggingLevel (platform parameters) is set to debug (default is info)
    
        self.log_debug("this is an debug message") # logs info into Logs/ThirdParty/MyRotator.log if logging level is set to debug

    =============================
    REQUIRED TERMINATION SIGNALS
    =============================
    Terminate signals -> MUST use one of the following three signals to terminate the script:

        self.close_success() # terminate with success state
        self.close_fail() # terminate with recoverable failed state
        self.close_fail(unrecoverable=True) # terminate with unrecoverable failed state

    When calling a signal sys.exit is invoked and the script is terminated.  If no signal is called, and the script finishes without any exception, it will behave like p4cpm.close_fail(unrecoverable=True) and log an error message.
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
        self.close_success() # terminate with success state if nothing needs to be done with a given action.

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
            # TODO: use self.args.username, self.args.address, self.args.port, self.secrets.password.get()
            # for your logic in a verification
        else:
            pass
            # TODO: use self.args.address, self.args.reconcile_username, self.secrets.reconcile_password.get()
            # for your logic in a verification
        result = True
        if result is True:
            self.log_info("verification successful") # logs info message into Logs/ThirdParty/MyRotator.log
        else:
            self.log_error("something went wrong") # logs error message Logs/ThirdParty/MyRotator.log
            self.close_fail()

    def _change(self, from_reconcile=False):
        if from_reconcile is False:
            pass
            # TODO: use self.args.username, self.args.address, self.args.port, self.secrets.password.get()
            # and self.secrets.new_password.get() for your logic in a rotation
        else:
            pass
            # TODO: use self.args.username, self.args.address, self.args.port, self.args.reconcile_username,
            # self.secrets.reconcile_password.get() and self.secrets.new_password.get() for your logic in a reconciliation
        result = True
        if result is True:
            self.log_info("rotation successful") # logs info message into Logs/ThirdParty/MyRotator.log
        else:
            self.log_error("something went wrong") # logs error message Logs/ThirdParty/MyRotator.log
            self.close_fail()


if __name__ == "__main__":
    MyRotator().run() # initializes the class and calls the action that was requested from CPM/SRS.
```
(*) More realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples/python4cpmhandler).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify -> the sciprt will be executed once running the `MyRotator.verify()` method.
2. Change -> the sciprt will be executed twice, running first the `MyRotator.logon()` method and secondly the `MyRotator.change()` method.
    - If both actions are not terminated with `self.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `self.close_fail(unrecoverable=True)`.
3. Reconcile -> the sciprt will be executed twice, running first the `MyRotator.prereconcile()` method and secondly the `MyRotator.reconcile()` method.
    - If both actions are not terminated with `self.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `self.close_fail(unrecoverable=True)`.
4. When calling `MyRotator.verify()`, `MyRotator.logon()` or `MyRotator.prereconcile()`: `self.secrets.new_password.get()` will always return an empty string.
5. If a logon account is not linked, `self.args.logon_username` and `self.secrets.logon_password.get()` will return empty strings.
6. If a reconcile account is not linked, `self.args.reconcile_username` and `self.secrets.reconcile_password.get()` will return empty strings.


### Using Python4CPM properties and methods directly (for low level controls):

```python
from python4cpm import Python4CPM


p4cpm = Python4CPM("MyApp") # this instantiates the object and grabs all arguments and secrets shared by the .NET SDK

# These are the usable properties and related methods from the object:
p4cpm.args.action # action requested from CPM/SRS
p4cpm.args.username # username from the account username field
p4cpm.args.address # address from the account address field
p4cpm.args.port # port from the account port field
p4cpm.args.reconcile_username # reconcile username from the linked reconcile account
p4cpm.args.logon_username # logon username from the linked logon account
p4cpm.args.logging # used to carry the platform logging settings for python
p4cpm.secrets.password.get() # get str from password received from the vault
p4cpm.secrets.new_password.get() # get str from new password in case of a rotation
p4cpm.secrets.logon_password.get() # get str from linked logon account password
p4cpm.secrets.reconcile_password.get() # get str from linked reconcile account password

# Logging methods -> Will only log if PythonLogging (platform parameters) is set to yes (default is yes)
p4cpm.log_error("this is an error message") # logs error into Logs/ThirdParty/MyApp.log
p4cpm.log_warning("this is a warning message") # logs warning into Logs/ThirdParty/MyApp.log
p4cpm.log_info("this is an info message") # logs info into Logs/ThirdParty/MyApp.log
# Logging level -> Will only log debug messages if PythonLoggingLevel (platform parameters) is set to debug (default is info)
p4cpm.log_debug("this is an debug message") # logs info into Logs/ThirdParty/MyApp.log if logging level is set to debug

# Terminate signals -> MUST use one of the following three signals to terminate the script:
## p4cpm.close_success() # terminate with success state
## p4cpm.close_fail() # terminate with recoverable failed state
## p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
# When calling a signal sys.exit is invoked and the script is terminated.  If no signal is called, and the script finishes without any exception, it will behave like p4cpm.close_fail(unrecoverable=True) and log an error message.


# Verification example -> verify the username and password are valid
def verify(from_reconcile=False):
    if from_reconcile is False:
        pass
        # TODO: use p4cpm.args.username, p4cpm.args.address, p4cpm.args.port, p4cpm.secrets.password.get()
        # for your logic in a verification
    else:
        pass
        # TODO: use p4cpm.args.address, p4cpm.args.port, p4cpm.args.reconcile_username, p4cpm.secrets.reconcile_password.get()
        # for your logic in a verification
    result = True
    if result is True:
        p4cpm.log_info("verification successful")
    else:
        p4cpm.log_error("something went wrong")
        raise Exception("verify failed") # raise to trigger failed termination signal


# Rotation example -> rotate the password of the account
def change(from_reconcile=False):
    if from_reconcile is False:
        pass
        # TODO: use p4cpm.args.username, p4cpm.args.address, p4cpm.args.port, p4cpm.secrets.password.get()
        # and p4cpm.secrets.new_password.get() for your logic in a rotation
    else:
        pass
        # TODO: use p4cpm.args.username, p4cpm.args.address, p4cpm.args.port, p4cpm.args.reconcile_username,
        # p4cpm.secrets.reconcile_password.get() and p4cpm.secrets.new_password.get() for your logic in a reconciliation
    result = True
    if result is True:
        p4cpm.log_info("rotation successful")
    else:
        p4cpm.log_error("something went wrong")
        raise Exception("change failed") # raise to trigger failed termination signal


if __name__ == "__main__":
    try:
        if p4cpm.args.action == Python4CPM.ACTION_VERIFY: # class attribute ACTION_VERIFY holds the verify action value
            verify()
            p4cpm.close_success()
        elif p4cpm.args.action == Python4CPM.ACTION_LOGON: # class attribute ACTION_LOGON holds the logon action value
            p4cpm.close_success() # terminate with success state if nothing needs to be done with a given action.
        elif p4cpm.args.action == Python4CPM.ACTION_CHANGE: # class attribute ACTION_CHANGE holds the password change action value
            change()
            p4cpm.close_success()
        elif p4cpm.args.action == Python4CPM.ACTION_PRERECONCILE: # class attribute ACTION_PRERECONCILE holds the pre-reconcile action value
            verify(from_reconcile=True)
            p4cpm.close_success()
            # Alternatively ->
            ## p4cpm.log_error("reconciliation is not supported") # let the logs know that reconciliation is not supported
            ## p4cpm.close_fail() # let CPM/SRS know to check the logs
        elif p4cpm.args.action == Python4CPM.ACTION_RECONCILE: # class attribute ACTION_RECONCILE holds the reconcile action value
            change(from_reconcile=True)
            p4cpm.close_success()
            # Alternatively ->
            ## p4cpm.log_error("reconciliation is not supported") # let the logs know that reconciliation is not supported
            ## p4cpm.close_fail() # let CPM/SRS know to check the logs
    except Exception as e:
        p4cpm.log_error(f"{type(e).__name__}: {e}")
        raise e # CPM/SRS will see any Exception as a p4cpm.close_fail(unrecoverable=True)
```
(*) More realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples/python4cpm).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify -> the sciprt will be executed once with the `p4cpm.args.action` as `Python4CPM.ACTION_VERIFY`.
2. Change -> the sciprt will be executed twice, once with the action `p4cpm.args.action` as `Python4CPM.ACTION_LOGON` and once as `Python4CPM.ACTION_CHANGE`.
    - If both actions are not terminated with `p4cpm.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `p4cpm.close_fail(unrecoverable=True)`.
3. Reconcile -> the sciprt will be executed twice, once with the `p4cpm.args.action` as `Python4CPM.ACTION_PRERECONCILE` and once as `Python4CPM.ACTION_RECONCILE`.
    - If both actions are not terminated with `p4cpm.close_success()` and the scripts terminates without any exception, CPM/SRS will see this as a `p4cpm.close_fail(unrecoverable=True)`.
4. When `p4cpm.args.action` comes as `Python4CPM.ACTION_VERIFY`, `Python4CPM.ACTION_LOGON` or `Python4CPM.ACTION_PRERECONCILE`: `p4cpm.secrets.new_password.get()` will always return an empty string.
5. If a logon account is not linked, `p4cpm.args.logon_username` and `p4cpm.secrets.logon_password.get()` will return empty strings.
6. If a reconcile account is not linked, `p4cpm.args.reconcile_username` and `p4cpm.secrets.reconcile_password.get()` will return empty strings.


### Installing dependencies in python venv

As with any python venv, you can install dependencies in your venv.
1. If your CPM can connect to the internet:
   - You can use regular pip install commands (e.g., `c:\venv\Scripts\pip.exe install requests`).
2. If your CPM cannot connect to the internet:
   - You can download packages for an offline install.  More info [here](https://pip.pypa.io/en/stable/cli/pip_download/).


## Dev Helper:

For dev purposes, `NETHelper` is a companion helper that simplifies the instantiation of the `Python4CPM` or `Python4CPMHandler` objects by simulating how the plugin passes arguments and secrets to the modules.
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
password = getpass("password: ") # password from account
logon_password = getpass("logon_password: ") # password from linked logon account
reconcile_password = getpass("reconcile_password: ") # password from linked reconcile account
new_password = getpass("new_password: ") # new password for the rotation

NETHelper.set(
    action=Python4CPM.ACTION_LOGON, # use actions from Python4CPM.ACTION_*
    username="jdoe", # populate with the username from your account properties
    address="myapp.corp.local", # populate with the address from your account properties
    port="8443", # populate with the port from your account properties
    logon_username="ldoe", # populate with the logon account username from your linked logon account
    reconcile_username="rdoe", # ppopulate with the reconcile account username from your linked logon account
    logging="yes", # populate with the PythonLogging parameter from the platform: "yes" or "no"
    logging_level="info", # populate with the PythonLoggingLevel parameter from the platform: "info" or "debug"
    password=password,
    logon_password=logon_password,
    reconcile_password=reconcile_password,
    new_password=new_password
)
```

#### Using the handler (recommended):

```python
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

#### Using Python4CPM properties and methods directly:

```python
p4cpm = NETHelper.get()

# TODO: use the p4cpm object during dev to build your script logic
assert password == p4cpm.secrets.password.get()
p4cpm.log_info("success!")
p4cpm.close_success()
```

#### Remember for your final script:

- Remove the import of `NETHelper`.
- Remove the `NETHelper.set()` call.
- If applicable, change the definition of `p4cpm` from `p4cpm = NETHelper.get()` to `p4cpm = Python4CPM("MyApp")`.
- Remove any secrets prompting or interactive interruptions.
