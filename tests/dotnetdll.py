
from configparser import ConfigParser
from python4cpm import Python4CPM
from tempfile import NamedTemporaryFile
from io import StringIO
import pytest
import os
import sys
import subprocess


def get_user_ini():
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


PLUGIN_INVOKER_PATH, PYTHON4CPM_DLL_PATH = get_framework_paths()
SUCCESS_CODE = 0
FAILED_RECOVERABLE_CODE = 8100
FAILED_UNRECOVERABLE_CODE = 8900
_SCRIPTS_PATH = get_scripts_path()
SCRIPTS_AND_CODES = {
    os.path.join(_SCRIPTS_PATH, "fail_recoverable.py"): FAILED_RECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "fail_unrecoverable.py"): FAILED_UNRECOVERABLE_CODE,
    os.path.join(_SCRIPTS_PATH, "success.py"): SUCCESS_CODE,
    os.path.join(_SCRIPTS_PATH, "unexpected_exception.py"): FAILED_UNRECOVERABLE_CODE,
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
ENV_MAPPINGS_ASSERTIONS_RESULTS = os.path.join(
    get_scripts_path(),
    "assert_env_mappings.assertions"
)


@pytest.mark.parametrize("python_path,script,action", PARAMS)
def test_python4cpm_dll_returns(python_path, script, action):
    print(f"action -> {action}")
    print(f"script -> {script}")
    config = get_user_ini()
    config.set("extrainfo", "PythonExePath", python_path)
    config.set("extrainfo", "PythonScriptPath", script)
    buffer = StringIO()
    config.write(buffer)
    _config = buffer.getvalue().split("\n", 1)[1]
    print(f"config -> \n{_config}")
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
    print(f"cmd -> {' '.join(cmd)}")
    result = subprocess.run(cmd) # noqa S603
    print(f"return code -> {result.returncode}")
    if python_path == PYTHON_PATHS[0]:
        assert result.returncode == SCRIPTS_AND_CODES[script] # noqa: S101
    else:
        assert result.returncode == FAILED_UNRECOVERABLE_CODE # noqa: S101


def test_env_mappings():
    action = Python4CPM.ACTION_VERIFY
    script = os.path.join(_SCRIPTS_PATH, "assert_env_mappings.py")
    print(f"action -> {action}")
    print(f"script -> {script}")
    config = get_user_ini()
    config.set("extrainfo", "PythonExePath", PYTHON_PATHS[0])
    config.set("extrainfo", "PythonScriptPath", script)
    buffer = StringIO()
    config.write(buffer)
    _config = buffer.getvalue().split("\n", 1)[1]
    print(f"config -> \n{_config}")
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
    print(f"cmd -> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True) # noqa S603
    print(f"return code -> {result.returncode}")
    if result.returncode != SUCCESS_CODE:
        with open(ENV_MAPPINGS_ASSERTIONS_RESULTS, "r") as f:
            print(f.read())
        raise AssertionError
