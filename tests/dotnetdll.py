
from configparser import ConfigParser
from python4cpm import Python4CPM
from python4cpm.logger import Logger
from tempfile import NamedTemporaryFile
from io import StringIO
import pytest
import os
import sys
import subprocess


def get_config_from_ini():
    file_dir = os.path.dirname(__file__)
    ini_path = os.path.join(file_dir, "sources", "User.ini")
    config = ConfigParser()
    config.optionxform = str
    with open(ini_path) as f:
        config.read_string("[DEFAULT]\n" + f.read())
    return config


def get_framework_paths():
    file_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(file_dir)
    framework_dir = os.path.join(root_dir, "_python4cpm", "framework")
    plugin_invoker_path = os.path.join(framework_dir, "CANetPluginInvoker.exe")
    python4cpm_dll_path = os.path.join(
        framework_dir,
        "CyberArk.Extensions.Plugin.Python4CPM.dll"
    )
    return plugin_invoker_path, python4cpm_dll_path


def get_scripts_path():
    file_dir = os.path.dirname(__file__)
    return os.path.join(file_dir, "dotnetdll-scripts")


LOGGER = Logger.get_logger(
    os.path.basename(__file__),
    list(Logger._LOGGING_LEVELS.keys())[0]
)
PLUGIN_INVOKER_PATH, PYTHON4CPM_DLL_PATH = get_framework_paths()
SUCCESS_CODE = 0
FAILED_RECOVERABLE_CODE = 8100
FAILED_UNRECOVERABLE_CODE = 8900
_SCRIPTS_PATH = get_scripts_path()
SCRIPTS_AND_CODES = {
    os.path.join(_SCRIPTS_PATH, "bad_handler.py"): FAILED_UNRECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "fail_recoverable_handler.py"): FAILED_RECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "fail_unrecoverable_handler.py"): FAILED_UNRECOVERABLE_CODE, # noqa E501
    os.path.join(_SCRIPTS_PATH, "success_handler.py"): SUCCESS_CODE,
    os.path.join(_SCRIPTS_PATH, "fail_recoverable.py"): FAILED_RECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "fail_unrecoverable.py"): FAILED_UNRECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "success.py"): SUCCESS_CODE,
    os.path.join(_SCRIPTS_PATH, "unexpected_exception.py"): FAILED_UNRECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "no_close_signal.py"): FAILED_UNRECOVERABLE_CODE,
    "nonexistent": FAILED_UNRECOVERABLE_CODE
}
PYTHON_PATHS = [
    sys.executable,
    "nonexistent"
]
ACTIONS = (
    Python4CPM.ACTION_VERIFY,
    Python4CPM.ACTION_LOGON,
    Python4CPM.ACTION_CHANGE,
    Python4CPM.ACTION_RECONCILE,
    Python4CPM.ACTION_PRERECONCILE
)
PARAMS = [
    (python_path, script, action)
    for action in ACTIONS
    for script in SCRIPTS_AND_CODES
    for python_path in PYTHON_PATHS
]


@pytest.mark.parametrize("python_path,script,action", PARAMS)
def test_python4cpm_dll_returns(python_path, script, action):
    LOGGER.info(f"action -> {action}")
    LOGGER.info(f"script -> {script}")
    config = get_config_from_ini()
    config.set("extrainfo", "PythonExePath", python_path)
    config.set("extrainfo", "PythonScriptPath", script)
    buffer = StringIO()
    config.write(buffer)
    _config = buffer.getvalue().split("\n", 1)[1]
    LOGGER.info(f"config -> \n{_config}")
    tmp = NamedTemporaryFile(mode="w", suffix=".ini", delete=False)
    tmp.write(_config)
    tmp.close()
    cmd = [
        PLUGIN_INVOKER_PATH,
        tmp.name,
        action,
        PYTHON4CPM_DLL_PATH,
        "True"
    ]
    LOGGER.info(f"cmd -> {' '.join(cmd)}")
    result = subprocess.run(cmd) # noqa S603
    LOGGER.info(f"return code -> {result.returncode}")
    if python_path == PYTHON_PATHS[0]:
        assert result.returncode == SCRIPTS_AND_CODES[script] # noqa: S101
    else:
        assert result.returncode == FAILED_UNRECOVERABLE_CODE # noqa: S101


def test_python4cpm_dll_env_mappings():
    action = Python4CPM.ACTION_CHANGE
    script = os.path.join(_SCRIPTS_PATH, "assert_env_mappings.py")
    LOGGER.info(f"action -> {action}")
    LOGGER.info(f"script -> {script}")
    config = get_config_from_ini()
    config.set("extrainfo", "PythonExePath", PYTHON_PATHS[0])
    config.set("extrainfo", "PythonScriptPath", script)
    buffer = StringIO()
    config.write(buffer)
    _config = buffer.getvalue().split("\n", 1)[1]
    LOGGER.info(f"config -> \n{_config}")
    tmp = NamedTemporaryFile(mode="w", suffix=".ini", delete=False)
    tmp.write(_config)
    tmp.close()
    cmd = [
        PLUGIN_INVOKER_PATH,
        tmp.name,
        action,
        PYTHON4CPM_DLL_PATH,
        "True"
    ]
    LOGGER.info(f"cmd -> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True) # noqa S603
    LOGGER.info(f"return code -> {result.returncode}")
    assert result.returncode == SUCCESS_CODE # noqa S603
