from python4cpm import Python4CPM
from python4cpm.logger import Logger
from configparser import ConfigParser
import os


LOGGER = Logger.get_logger(
    os.path.basename(__file__),
    Logger._LOGGING_ENABLED_VALUE,
    list(Logger._LOGGING_LEVELS.keys())[0]
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
    p4cpm = Python4CPM(os.path.basename(__file__))
    config = get_config_from_ini()
    assertions = (
        (p4cpm.args.action, Python4CPM.ACTION_VERIFY),
        (p4cpm.args.address, config["DEFAULT"]["address"]),
        (p4cpm.args.username, config["DEFAULT"]["username"]),
        (p4cpm.args.port, config["DEFAULT"]["port"]),
        (p4cpm.args.logon_username, config["extrapass1"]["username"]),
        (p4cpm.args.reconcile_username, config["extrapass3"]["username"]),
        (p4cpm.args.logging, config["extrainfo"]["PythonLogging"]),
        (p4cpm.args.logging_level, config["extrainfo"]["PythonLoggingLevel"]),
        (p4cpm.secrets.password.get(), config["DEFAULT"]["password"]),
        (p4cpm.secrets.logon_password.get(), config["extrapass1"]["password"]),
        (p4cpm.secrets.reconcile_password.get(), config["extrapass3"]["password"]),
    )
    for a, b in assertions:
        LOGGER.info(f"Asserting '{a}' == '{b}'...")
        if a != b:
            LOGGER.error("Assertion failed")
            raise AssertionError
    p4cpm.close_success()
except Exception as e:
    LOGGER.error(f"{type(e).__name__}: {e}")
    raise e
