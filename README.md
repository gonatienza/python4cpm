# Python4CPM

A simple way of using python scripts for CyberArk CPM rotations

## Installation

```bash
pip install git+https://github.com/gonatienza/python4cpm
```
or
```bash
pip install https://github.com/gonatienza/python4cpm/archive/refs/tags/latest.tar.gz
```

## Usage

### Examples:

```python
from python4cpm import Python4CPM


p4cpm = Python4CPM("MyApp")

# These are the usable properties from the object:
p4cpm.args.action # action requested from CPM
p4cpm.args.address # address from the account address field
p4cpm.args.username # username from the account username field
p4cpm.args.reconcile_username # reconcile username from the linked reconcile account
p4cpm.args.logon_username # logon username from the linked logon account
p4cpm.args.logging # used to carry the platform logging settings for python
p4cpm.secrets.password # password received from the vault
p4cpm.secrets.new_password # new password in case of a rotation
p4cpm.secrets.logon_password # linked logon account password
p4cpm.secrets.reconcile_password # linked reconcile account password


def change():
    # use p4cpm.args.address, p4cpm.args.username, p4cpm.secrets.password 
    # and p4cpm.secrets.new_password for your logic in a rotation
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
