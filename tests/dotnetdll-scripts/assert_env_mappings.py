from python4cpm import Python4CPM
from configparser import ConfigParser
import os


ENV_MAPPINGS_ASSERTIONS_RESULTS = os.path.join(
    os.path.dirname(__file__),
    "assert_env_mappings.log"
)


def append_to_assertions_results(message):
    with open(ENV_MAPPINGS_ASSERTIONS_RESULTS, "a") as f:
            f.write(f"{message}\n")


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
    p4cpm = Python4CPM(__file__)
    config = get_config_from_ini()
    assertions = (
        (p4cpm.args.action, Python4CPM.ACTION_VERIFY),
        (p4cpm.args.address, config["DEFAULT"]["address"]),
        (p4cpm.args.logon_username, config["extrapass1"]["username"]),
        (p4cpm.args.reconcile_username, config["extrapass3"]["username"]),
        (p4cpm.args.logging, config["extrainfo"]["PythonLogging"]),
        (p4cpm.args.logging_level, config["extrainfo"]["PythonLoggingLevel"]),
        (p4cpm.secrets.password.get(), config["DEFAULT"]["password"]),
        (p4cpm.secrets.logon_password.get(), config["extrapass1"]["password"]),
        (p4cpm.secrets.reconcile_password.get(), config["extrapass3"]["password"]),
    )
    for a, b in assertions:
        append_to_assertions_results(f"Asserting '{a}' == '{b}'...")
        if a != b:
            append_to_assertions_results("Assertion failed")
            raise AssertionError
    p4cpm.close_success()
except Exception as e:
    append_to_assertions_results(f"{type(e).__name__}: {e}")
    raise e
