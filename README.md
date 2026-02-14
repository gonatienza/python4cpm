# Python4CPM

A simple way of using python scripts with CyberArk CPM rotations.  This module levereages the [Terminal Plugin Controller](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/plug-in-terminal-plugin-controller.htm) (TPC) in CPM to offload a password rotation logic into a script.

This platform allows you to duplicate it multiple times, simply changing its settings from Privilege Cloud/PVWA to point to different python scripts leveraging the module included with the base platform.

## Installation

1. Install Python in CPM.  **IMPORTANT:** *Python must be installed for all users when running the install wizard*.
2. Run in CPM (from powershell or cmd) `py -m venv c:\venv` to create a venv.  Use the default location `c:\venv` or a custom one (e.g., `c:\my-venv-path`).
3. Download the latest platform [zip file](https://github.com/gonatienza/python4cpm/releases/download/latest/python4cpm.zip).
4. Import the platform zip file into Privilege Cloud/PVWA `(Administration -> Platform Management -> Import platform)`.
5. Craft your python script and place it within the bin folder of CPM (`C:\Program Files (x86)\CyberArk\Password Manager\bin`).
6. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
7. Edit the duplicated platform and specify the path of your placed script in the bin folder of CPM, under `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonScriptPath -> Value` (e.g., `bin\myapp.py`).
8. If you used a custom location in step 2, also update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonExePath -> Value` with the custom path for the venv's `python.exe` file (e.g., `c:\my-venv-path\Scripts\python.exe`).
9. If you want to disable logging, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLogging -> Value` to `no`.
10. If you want to change the logging level to `debug`, update `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLoggingLevel -> Value` to `debug`.
11. For new applications repeat steps from 5 to 10.


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

# Logging methods -> Will only log if Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonLogging is set to yes (default)
p4cpm.log_error("something went wrong") # logs error into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_warning("this is a warning") # logs warning into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_info("this is an info message") # logs info into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_debug("this is an debug message") # logs info into Logs/ThirdParty/Python4CPM/MyApp.log if logging level is set to debug

# Terminate signals -> ALWAYS use one of the following three signals to terminate the script
## p4cpm.close_success() # terminate with success state
## p4cpm.close_fail() # terminate with recoverable failed state
## p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
# If no signal is call, CPM will not know if the action was successful and display an error


# Rotation example
def change():
    # Use p4cpm.args.address, p4cpm.args.username, p4cpm.secrets.password.get()
    # and p4cpm.secrets.new_password.get() for your logic in a rotation
    result = True
    if result is True:
        p4cpm.log_info("rotation successful") # logs info message into Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_success() # terminate with success state
    else:
        p4cpm.log_error("something went wrong") # logs into message Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_fail() # terminate with recoverable failed state


if __name__ == "__main__":
    action = p4cpm.args.action

    if action == Python4CPM.ACTION_VERIFY: # attribute holds the verify action value
        p4cpm.close_fail() # let CPM know there is no logic for this action
    elif action == Python4CPM.ACTION_LOGON: # attribute holds the logon action value
        p4cpm.close_fail() # let CPM know there is no logic for this action
    elif action == Python4CPM.ACTION_CHANGE: # attribute holds the password change action value
        change()
    elif action == Python4CPM.ACTION_PRERECONCILE: # attribute holds the pre-reconcile action value
        p4cpm.close_fail() # let CPM know there is no logic for this action
    elif action == Python4CPM.ACTION_RECONCILE: # attribute holds the reconcile action value
        p4cpm.close_fail() # let CPM know there is no logic for this action
    else:
        p4cpm.log_error(f"invalid action: '{action}'") # logs into Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
```
(*) a more realistic examples can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples).

When doing `verify`, `change` or `reconcile` from Privilege Cloud/PVWA:
1. Verify action -> the sciprt will be executed once with the `p4cpm.args.action` as `Python4CPM.ACTION_VERIFY`.
2. Change action -> the sciprt will be executed twice, once with the action `p4cpm.args.action` as `Python4CPM.ACTION_LOGON` and once as `Python4CPM.ACTION_CHANGE`.
3. Reconcile action -> the sciprt will be executed twice, once with the `p4cpm.args.action` as `Python4CPM.ACTION_PRERECONCILE` and once as `Python4CPM.ACTION_RECONCILE`.
4. When `p4cpm.args.action` comes as `Python4CPM.ACTION_VERIFY`, `Python4CPM.ACTION_LOGON` and `Python4CPM.ACTION_PRERECONCILE`, `p4cpm.secrets.new_password.get()` will always return an empty string.
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
This is only available if you install this module (in a dev workstation) with:

```bash
pip install git+https://github.com/gonatienza/python4cpm
```
or
```bash
pip install https://github.com/gonatienza/python4cpm/archive/refs/tags/latest.tar.gz
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
# changing the definition of p4cpm from TPCHelper.run() to Python4CPM("MyApp")
# remove any secrets prompting
# remove the TPCHelper import
```
