from python4cpm import Python4CPM
from python4cpm.logger import Logger
from configparser import ConfigParser
import os


LOGGER = Logger.get_logger(os.path.basename(__file__), "debug")
ACTIONS_WITH_NEW_PASSWORD = (
    Python4CPM.ACTION_CHANGE,
    Python4CPM.ACTION_RECONCILE
)


def get_config_from_ini():
    file_dir = os.path.dirname(__file__)
    tests_dir = os.path.dirname(file_dir)
    ini_path = os.path.join(tests_dir, "sources", "User.ini")
    config = ConfigParser()
    config.optionxform = str
    with open(ini_path) as f:
        config.read_string("[DEFAULT]\n" + f.read())
    return config


try:
    p4cpm = Python4CPM()
    config = get_config_from_ini()
    action = os.environ.get("PYTHON4CPM_PYTEST_ACTION")
    assertions = [
        (p4cpm.args.action, action),
        (p4cpm.args.logging_level, config["extrainfo"]["PythonLoggingLevel"]),
        (p4cpm.target_account.policy_id, config["DEFAULT"]["PolicyID"]),
        (p4cpm.target_account.object_name, config["DEFAULT"]["objectname"]),
        (p4cpm.target_account.username, config["DEFAULT"]["username"]),
        (p4cpm.target_account.address, config["DEFAULT"]["address"]),
        (p4cpm.target_account.port, config["DEFAULT"]["port"]),
        (p4cpm.logon_account.username, config["extrapass1"]["username"]),
        (p4cpm.reconcile_account.username, config["extrapass3"]["username"]),
        (p4cpm.target_account.password.get(), config["DEFAULT"]["password"]),
        (p4cpm.logon_account.password.get(), config["extrapass1"]["password"]),
        (p4cpm.reconcile_account.password.get(), config["extrapass3"]["password"])
    ]
    for a, b in assertions:
        if a != b:
            raise AssertionError(f"Assertion failed '{a}' == '{b}'")
        LOGGER.info(f"Asserted '{a}' == '{b}'")
    if p4cpm.args.action in ACTIONS_WITH_NEW_PASSWORD:
        a = p4cpm.target_account.new_password.get()
        b = config["DEFAULT"]["newpassword"]
        if a != b:
            raise AssertionError(f"Assertion failed '{a}' == '{b}'")
        LOGGER.info(f"Asserted '{a}' == '{b}'")
    else:
        if p4cpm.target_account.new_password is not None:
            LOGGER.error("target_account.new_password is not None")
            raise AssertionError
        LOGGER.info(f"Asserted '{p4cpm.target_account.new_password}' is 'None'")
    p4cpm.close_success()
except Exception as e:
    LOGGER.error(f"{type(e).__name__}: {e}")
    raise e
