# Python4CPM

A simple way of using python scripts with CyberArk CPM rotations.  This module levereages the [Terminal Plugin Controller](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/plug-in-terminal-plugin-controller.htm) (TPC) in CPM to offload a password rotation logic into a script.

This platform allows you to duplicate it multiple times, simply changing its settings from Privilege Cloud/PVWA to point to different python scripts leveraging the module included with the base platform.

## Installation

1. Install Python in CPM.  **IMPORTANT:** *Python must be installed for all users when running the install wizard*.
2. Run in CPM (from powershell or cmd) `py -m venv c:\venv` to create a venv.
3. Download the latest platform [zip file](https://github.com/gonatienza/python4cpm/releases/download/latest/python4cpm.zip).
4. Import the platform zip file into Privilege Cloud/PVWA `(Administration -> Platform Management -> Import platform)`.
5. Craft your python script and place it within the bin folder of CPM (`C:\Program Files (x86)\CyberArk\Password Manager\bin`).
6. Duplicate the imported platform in Privilege Cloud/PVWA `(Administration -> Platform Management -> Application -> Python for CPM)` and name it after your application (e.g., My App).
7. Edit the duplicated platform and specify the path of your placed script in the bin folder of CPM, under `Target Account Platform -> Automatic Platform Management -> Additional Policy Settings -> Parameters -> PythonScriptPath -> Value` (e.g., `bin\myapp.py`).
8. For new applications repeat steps from 5 to 7.


## Python Script

### Example:

```python
from python4cpm import Python4CPM


p4cpm = Python4CPM("MyApp") # this initiates the object and grabs all arguments and secrets shared by TPC

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

# These are the other methods from the object to keep in mind:
p4cpm.log_error("something went wrong") # logs error into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_warning("this is a warning") # logs warning into Logs/ThirdParty/Python4CPM/MyApp.log
p4cpm.log_error("this is an info message") # logs info into Logs/ThirdParty/Python4CPM/MyApp.log

# Terminate signals -> ALWAYS use one of the following three signals to terminate the script.
## p4cpm.close_success() # terminate with success state
## p4cpm.close_fail() # terminate with recoverable failed state
## p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state


def change():
    # use p4cpm.args.address, p4cpm.args.username, p4cpm.secrets.password.get()
    # and p4cpm.secrets.new_password.get() for your logic in a rotation
    result = True
    if result is True:
        p4cpm.log_info("rotation successful") # logs into Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_success() # terminate with success state
    else:
        p4cpm.log_error("something went wrong") # logs into Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_fail() # terminate with recoverable failed state


if __name__ == "__main__":
    action = p4cpm.args.action
    if action == p4cpm.ACTION_VERIFY: # attribute holds the verify action value
        pass
    elif action == p4cpm.ACTION_LOGON: # attribute holds the logon action value
        pass
    elif action == p4cpm.ACTION_CHANGE: # attribute holds the password change action value
        change()
    elif action == p4cpm.ACTION_PRERECONCILE: # attribute holds the pre-reconcile action value
        pass
    elif action == p4cpm.ACTION_RECONCILE: # attribute holds the reconcile action value
        pass
    else:
        p4cpm.log_error(f"invalid action: '{action}'") # logs into Logs/ThirdParty/Python4CPM/MyApp.log
        p4cpm.close_fail(unrecoverable=True) # terminate with unrecoverable failed state
```
When doing verify, change or reconcile from Privilege Cloud:
1. Verify -> the sciprt will be executed once with the `p4cpm.args.action` as `p4cpm.ACTION_VERIFY`.
2. Change -> the sciprt will be executed twice, once with the action `p4cpm.args.action` as `p4cpm.ACTION_LOGON` and once as `p4cpm.ACTION_CHANGE`.
3. Reconcile -> the sciprt will be executed twice, once with the `p4cpm.args.action` as `p4cpm.ACTION_PRERECONCILE` and once as `p4cpm.ACTION_RECONCILE`.
4. When `p4cpm.args.action` comes as `p4cpm.ACTION_VERIFY`, `p4cpm.ACTION_LOGON` and `p4cpm.ACTION_PRERECONCILE`,`p4cpm.secrets.new_password.get()` will always return an empty string.
5. If a logon account is not linked, `p4cpm.args.logon_username` and `p4cpm.secrets.logon_password.get()` will return an empty string.
6. If a reconcile account is not linked, `p4cpm.args.reconcile_username` and `p4cpm.secrets.reconcile_password.get()` will return an empty string.

(*) a more realistic example can be found [here](https://github.com/gonatienza/python4cpm/blob/main/examples/credmanagement.py).


### Dev Helper:

Install this module anywhere with:

```bash
pip install git+https://github.com/gonatienza/python4cpm
```
or
```bash
pip install https://github.com/gonatienza/python4cpm/archive/refs/tags/latest.tar.gz
```

TPC is a binary Terminal Plugin Controller in CPM.  It passes information to Python4CPM through arguments and prompts when calling the script.  For testing purposes,  `TPCHelper` simplifies the creation of the `Python4CPM` object by simulating how TPC passes those arguments and prompts:

```python
from python4cpm import TPCHelper

p4cpm = TPCHelper.run(
    action="logon",
    address="myapp.corp.local",
    username="jdoe",
    logon_username="ldoe",
    reconcile_username="rdoe",
    logging="yes",
    password="mypass",
    logon_password="mylogonpass",
    reconcile_password="myreconcilepass",
    new_password="mynewpass"
)
```
