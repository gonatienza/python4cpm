# Python4CPM

A simple way of using python scripts with CyberArk CPM rotations.  This module levereages the [Terminal Plugin Controller](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/plug-in-terminal-plugin-controller.htm) (TPC) in CPM to offload a password rotation logic into a script.

This platform allows you to duplicate it multiple times, simply changing its settings from Privilege Cloud/PVWA to point to different python scripts leveraging the module `python4cpm`.

## Installation

### Preparing Python

1. Install Python in CPM.  **Python must be installed for all users when running the install wizard**.
2. Create a venv in CPM, by running `py -m venv c:\venv`.  Use the default location `c:\venv` or a custom one (e.g., `c:\my-venv-path`).
3. Install `python4cpm` in your venv:
    - If your CPM can connect to the internet, install with `c:\venv\Scripts\pip install python4cpm`.
    - If your CPM cannot connect to the internet:
        - Download the [latest wheel](https://github.com/gonatienza/python4cpm/releases/download/latest/python4cpm-wheel.zip).
        - Copy the file to CPM and extract to a temporary location.
        - From the temporary location run `c:\venv\Scripts\pip install --no-index --find-links=.\python4cpm-wheel python4cpm`.


### Importing the platform

1. Download the [latest platform zip file](https://github.com/gonatienza/python4cpm/releases/download/latest/python4cpm-platform.zip).
2. Import the platform zip file into Privilege Cloud/PVWA `(Administration -> Platform Management -> Import platform)`.
3. Craft your python script and place it within the bin folder of CPM (`C:\Program Files (x86)\CyberArk\Password Manager\bin`).
4. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
5. Edit the duplicated platform and specify the path of your placed script in the bin folder of CPM, under `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonScriptPath -> Value` (e.g., `bin\myapp.py`).
6. If you used a custom venv location, also update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonExePath -> Value` with the custom path for the venv's `python.exe` file (e.g., `c:\my-venv-path\Scripts\python.exe`).
7. If you want to disable logging, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLogging -> Value` to `no`.
8. If you want to change the logging level to `debug`, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLoggingLevel -> Value` to `debug`.
9. For new applications repeat steps from 3 to 8.


## Python Script

### Example:

```python
from python4cpm import Python4CPM


p4cpm = Python4CPM("MyApp") # this instantiates the object and grabs all arguments and secrets shared by TPC

# These are the usable properties and related methods from the object:
p4cpm.args.action # action requested from CPM
p4cpm.args.address # address from the account address field
p4cpm.args.username # username from the account username field
p4cpm.args.reconcile_username # reconcile username from the linked reconcile account
p4cpm.args.logon_username # logon username from the linked logon account
p4cpm.args.logging # used to carry the platform logging settings for python
p4cpm.secrets.password.get() # get str from password received from the vault
p4cpm.secrets.new_password.get() # get str from new password in case of a rotation
p4cpm.secrets.logon_password.get() # get str from linked logon account password
p4cpm.secrets.reconcile_password.get() # get str from linked reconcile account password

# Logging methods -> Will only log if Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLogging is set to yes (default is yes)
p4cpm.log_error("this is an error message") # logs error into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_warning("this is a warning message") # logs warning into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_info("this is an info message") # logs info into Logs/ThirdParty/Python4CPM/MyApp.log
# Logging level -> Will only log debug messages if Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLoggingLevel is set to debug (default is info)
p4cpm.log_debug("this is an debug message") # logs info into Logs/ThirdParty/Python4CPM/MyApp.log if logging level is set to debug

# Terminate signals -> ALWAYS use one of the following three signals to terminate the script
## p4cpm.close_success() # terminate with success state
## p4cpm.close_fail() # terminate with recoverable failed state
## p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
# If no signal is call, CPM will not know if the action was successful and display an error


# Verification example -> verify the username and password are valid
def verify(from_reconcile=False):
    if from_reconcile is False:
        pass
        # Use p4cpm.args.address, p4cpm.args.username, p4cpm.secrets.password.get()
        # for your logic in a verification
    else:
        pass
        # Use p4cpm.args.address, p4cpm.args.reconcile_username, p4cpm.secrets.reconcile_password.get()
        # for your logic in a verification
    result = True
    if result is True:
        p4cpm.log_info("verification successful") # logs info message into Logs/ThirdParty/Python4CPM/MyApp.log
    else:
        p4cpm.log_error("something went wrong") # logs error message Logs/ThirdParty/Python4CPM/MyApp.log
        raise Exception("verify failed") # raise to trigger failed termination signal


# Rotation example -> rotate the password of the account
def change(from_reconcile=False):
    if from_reconcile is False:
        pass
        # Use p4cpm.args.address, p4cpm.args.username, p4cpm.secrets.password.get()
        # and p4cpm.secrets.new_password.get() for your logic in a rotation
    else:
        pass
        # Use p4cpm.args.address, p4cpm.args.username, p4cpm.args.reconcile_username,
        # p4cpm.secrets.reconcile_password.get() and p4cpm.secrets.new_password.get() for your logic in a reconciliation
    result = True
    if result is True:
        p4cpm.log_info("rotation successful") # logs info message into Logs/ThirdParty/Python4CPM/MyApp.log
    else:
        p4cpm.log_error("something went wrong") # logs error message Logs/ThirdParty/Python4CPM/MyApp.log
        raise Exception("change failed") # raise to trigger failed termination signal


if __name__ == "__main__":
    try:
        if action == Python4CPM.ACTION_VERIFY: # class attribute ACTION_VERIFY holds the verify action value
            verify()
            p4cpm.close_success() # terminate with success state
        elif p4cpm.args.action == Python4CPM.ACTION_LOGON: # class attribute ACTION_LOGON holds the logon action value
            verify()
            p4cpm.close_success() # terminate with success state
        elif p4cpm.args.action == Python4CPM.ACTION_CHANGE: # class attribute ACTION_CHANGE holds the password change action value
            change()
            p4cpm.close_success() # terminate with success state
        elif p4cpm.args.action == Python4CPM.ACTION_PRERECONCILE: # class attribute ACTION_PRERECONCILE holds the pre-reconcile action value
            verify(from_reconcile=True)
            p4cpm.close_success() # terminate with success state
            # Alternatively ->
            ## p4cpm.log_error("reconciliation is not supported") # let the logs know that reconciliation is not supported
            ## p4cpm.close_fail() # let CPM know to check the logs
        elif p4cpm.args.action == Python4CPM.ACTION_RECONCILE: # class attribute ACTION_RECONCILE holds the reconcile action value
            change(from_reconcile=True)
            p4cpm.close_success() # terminate with success state
            # Alternatively ->
            ## p4cpm.log_error("reconciliation is not supported") # let the logs know that reconciliation is not supported
            ## p4cpm.close_fail() # let CPM know to check the logs
        else:
            p4cpm.log_error(f"invalid action: '{action}'") # logs into Logs/ThirdParty/Python4CPM/MyApp.log
            p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
    except Exception as e:
        p4cpm.log_error(f"{type(e).__name__}: {e}")
        p4cpm.close_fail()
```
(*) a more realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify -> the sciprt will be executed once with the `p4cpm.args.action` as `Python4CPM.ACTION_VERIFY`.
2. Change -> the sciprt will be executed twice, once with the action `p4cpm.args.action` as `Python4CPM.ACTION_LOGON` and once as `Python4CPM.ACTION_CHANGE`.
    - If all actions are not terminated with `p4cpm.close_success()` the overall change will fail.
3. Reconcile -> the sciprt will be executed twice, once with the `p4cpm.args.action` as `Python4CPM.ACTION_PRERECONCILE` and once as `Python4CPM.ACTION_RECONCILE`.
    - If all actions are not terminated with `p4cpm.close_success()` the overall reconcile will fail.
4. When `p4cpm.args.action` comes as `Python4CPM.ACTION_VERIFY`, `Python4CPM.ACTION_LOGON` or `Python4CPM.ACTION_PRERECONCILE`: `p4cpm.secrets.new_password.get()` will always return an empty string.
5. If a logon account is not linked, `p4cpm.args.logon_username` and `p4cpm.secrets.logon_password.get()` will return an empty string.
6. If a reconcile account is not linked, `p4cpm.args.reconcile_username` and `p4cpm.secrets.reconcile_password.get()` will return an empty string.


### Installing dependancies in python venv

As with any python venv, you can install dependancies in your venv.
1. If your CPM can connect to the internet:
   - You can use regular pip install commands (e.g., `c:\venv\Scripts\pip.exe install requests`).
2. If your CPM cannot connect to the internet:
   - You can download packages for an offline install.  More info [here](https://pip.pypa.io/en/stable/cli/pip_download/).


## Dev Helper:

TPC is a binary Terminal Plugin Controller in CPM.  It passes information to Python4CPM through arguments and prompts when calling the script.
For dev purposes, `TPCHelper` is a companion helper that simplifies the instantiation of the `Python4CPM` object by simulating how TPC passes those arguments and prompts.
Install this module (in a dev workstation) with:

```bash
pip install python4cpm
```

### Example:

```python
from python4cpm import TPCHelper, Python4CPM
from getpass import getpass

# Get secrets for your password, logon account password, reconcile account password and new password
# You can use an empty string if it does not apply
password = getpass("password: ") # password from account
logon_password = getpass("logon_password: ") # password from linked logon account
reconcile_password = getpass("reconcile_password: ") # password from linked reconcile account
new_password = getpass("new_password: ") # new password for the rotation

p4cpm = TPCHelper.run(
    action=Python4CPM.ACTION_LOGON, # use actions from Python4CPM.ACTION_*
    address="myapp.corp.local", # populate with the address from your account properties
    username="jdoe", # populate with the username from your account properties
    logon_username="ldoe", # populate with the logon account username from your linked logon account
    reconcile_username="rdoe", # ppopulate with the reconcile account username from your linked logon account
    logging="yes", # populate with the PythonLogging parameter from the platform: "yes" or "no"
    logging_level="info", # populate with the PythonLoggingLevel parameter from the platform: "info" or "debug"
    password=password,
    logon_password=logon_password,
    reconcile_password=reconcile_password,
    new_password=new_password
)

# Use the p4cpm object during dev to build your script logic
assert password == p4cpm.secrets.password.get()
p4cpm.log_info("success!")
p4cpm.close_success()

# Remember for your final script:
## changing the definition of p4cpm from TPCHelper.run() to Python4CPM("MyApp")
## remove any secrets prompting
## remove the TPCHelper import
```

Remember for your final script:
- Change the definition of `p4cpm` from `p4cpm = TPCHelper.run(**kwargs)` to `p4cpm = Python4CPM("MyApp")`.
- Remove any secrets prompting or interactive interruptions.
- Remove the import of `TPCHelper`.
