from python4cpm.python4cpm import Python4CPM
from python4cpm.python4cpmhandler import Python4CPMHandler
from python4cpm.accounts import TargetAccount, LogonAccount, ReconcileAccount
from python4cpm.secret import Secret
from python4cpm.args import Args
from python4cpm.crypto import Crypto
from python4cpm.nethelper import NETHelper
from python4cpm.logger import Logger
import json
import pytest
import os


def get_env():
    file_dir = os.path.dirname(__file__)
    env_path = os.path.join(file_dir, "sources", "env.json")
    with open(env_path, "r") as f:
        env = json.load(f)
    return env


LOGGER = Logger.get_logger(os.path.basename(__file__), "debug")
ENV = get_env()
LOGGING_LEVELS = ["ERROR", "debug", "bad"]
ARGS_PARAMS = [
    (action, logging_level)
    for logging_level in LOGGING_LEVELS
    for action in Python4CPM._VALID_ACTIONS
]
ACTIONS_WITH_NEW_PASSWORD = (
    Python4CPM.ACTION_CHANGE,
    Python4CPM.ACTION_RECONCILE
)
ACTIONS_WITHOUT_NEW_PASSWORD = (
    Python4CPM.ACTION_VERIFY,
    Python4CPM.ACTION_LOGON,
    Python4CPM.ACTION_PRERECONCILE
)
CLOSE_CODES = [
    Python4CPM._SUCCESS_CODE,
    Python4CPM._FAILED_RECOVERABLE_CODE,
    Python4CPM._FAILED_UNRECOVERABLE_CODE
]


class GoodClass(Python4CPMHandler):
    def verify(self):
        self.close_success()

    def logon(self):
        self.close_success()

    def change(self):
        self.close_success()

    def prereconcile(self):
        self.close_success()

    def reconcile(self):
        self.close_success()


class BadClassNoMethods(Python4CPMHandler):
    pass


@pytest.mark.parametrize("action,logging_level", ARGS_PARAMS)
def test_main(action, logging_level,  monkeypatch):
    env = {
        f"{Python4CPM._ENV_PREFIX}{key.upper()}": value
        for key, value in ENV.items()
    }
    env[Python4CPM._get_env_key(Args.ARGS[0])] = action
    env[Python4CPM._get_env_key(Args.ARGS[1])] = logging_level
    if Crypto.ENABLED:
        env_keys = (
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(LogonAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(ReconcileAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[4]),
        )
        for k in env_keys:
            env[k] = Crypto.encrypt(env[k])
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        env[Python4CPM._get_env_key(TargetAccount.ENV_VARS[4])] = ""
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_main.__name__)
    for k, v in vars(p4cpm.args).items():
        LOGGER.info(f"{k} -> {v}")
    accounts = (p4cpm.target_account, p4cpm.logon_account, p4cpm.reconcile_account)
    for account in accounts:
        for k, v in vars(account).items():
            if isinstance(v, Secret):
                v = v.get()
            LOGGER.info(f"{k} -> {v}")
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.target_account.username == ENV["target_username"] # noqa: S101
    assert p4cpm.target_account.address == ENV["target_address"] # noqa: S101
    assert p4cpm.target_account.port == ENV["target_port"] # noqa: S101
    assert p4cpm.logon_account.username == ENV["logon_username"] # noqa: S101
    assert p4cpm.reconcile_account.username == ENV["reconcile_username"] # noqa: S101
    assert p4cpm.target_account.password.get() == ENV["target_password"] # noqa: S101
    assert p4cpm.logon_account.password.get() == ENV["logon_password"] # noqa: S101
    assert p4cpm.reconcile_account.password.get() == ENV["reconcile_password"] # noqa: S101
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        assert p4cpm.target_account.new_password.get() == "" # noqa: S101
    else:
        assert p4cpm.target_account.new_password.get() == ENV["target_new_password"] # noqa: S101
    assert p4cpm._logger # noqa: S101
    if logging_level.lower() == LOGGING_LEVELS[1]:
        assert p4cpm._logger.level == Logger._LOGGING_LEVELS[LOGGING_LEVELS[1]] # noqa: S101
    else:
        assert p4cpm._logger.level == Logger._DEFAULT_LEVEL # noqa: S101
    with pytest.raises(SystemExit) as e:
        p4cpm.close_success() # avoiding stderr output
    assert e.value.code == CLOSE_CODES[0] # noqa: S101
    with pytest.raises(SystemExit):
        GoodClass().run()
    with pytest.raises(TypeError):
        BadClassNoMethods().run()


def test_handler_bad_action(monkeypatch):
    env = {
        f"{Python4CPM._ENV_PREFIX}{key.upper()}": value
        for key, value in ENV.items()
    }
    env[Python4CPM._get_env_key(Args.ARGS[0])] = "nonexistent"
    env[Python4CPM._get_env_key(Args.ARGS[1])] = LOGGING_LEVELS[1]
    if Crypto.ENABLED:
        env_keys = (
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(LogonAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(ReconcileAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[4]),
        )
        for k in env_keys:
            env[k] = Crypto.encrypt(env[k])
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    with pytest.raises(ValueError):
        GoodClass().run()


@pytest.mark.parametrize("close", CLOSE_CODES)
def test_exit_codes(close, monkeypatch, capsys):
    env = {
        f"{Python4CPM._ENV_PREFIX}{key.upper()}": value
        for key, value in ENV.items()
    }
    env[Python4CPM._get_env_key(Args.ARGS[0])] = Python4CPM.ACTION_CHANGE
    env[Python4CPM._get_env_key(Args.ARGS[1])] = LOGGING_LEVELS[1]
    if Crypto.ENABLED:
        env_keys = (
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(LogonAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(ReconcileAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[4]),
        )
        for k in env_keys:
            env[k] = Crypto.encrypt(env[k])
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_exit_codes.__name__)
    if close == CLOSE_CODES[0]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_success()
        assert e.value.code == CLOSE_CODES[0] # noqa: S101
    elif close == CLOSE_CODES[1]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_fail()
        assert e.value.code == CLOSE_CODES[1] # noqa: S101
    elif close == CLOSE_CODES[2]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_fail(unrecoverable=True)
        assert e.value.code == CLOSE_CODES[2] # noqa: S101


def test_on_exit_stderr(monkeypatch, capsys):
    env = {
        f"{Python4CPM._ENV_PREFIX}{key.upper()}": value
        for key, value in ENV.items()
    }
    env[Python4CPM._get_env_key(Args.ARGS[0])] = Python4CPM.ACTION_CHANGE
    env[Python4CPM._get_env_key(Args.ARGS[1])] = LOGGING_LEVELS[1]
    if Crypto.ENABLED:
        env_keys = (
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(LogonAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[1]),
            Python4CPM._get_env_key(TargetAccount.ENV_VARS[4]),
        )
        for k in env_keys:
            env[k] = Crypto.encrypt(env[k])
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_on_exit_stderr.__name__)
    p4cpm._on_exit()
    captured = capsys.readouterr()
    assert captured.err != "" # noqa: S101


def test_net_helper():
    action = Python4CPM.ACTION_CHANGE
    logging_level = LOGGING_LEVELS[1]
    NETHelper.set(
        action=action,
        target_address=ENV["target_address"],
        target_username=ENV["target_username"],
        target_port=ENV["target_port"],
        logon_username=ENV["logon_username"],
        reconcile_username=ENV["reconcile_username"],
        logging_level=logging_level,
        target_password=ENV["target_password"],
        logon_password=ENV["logon_password"],
        reconcile_password=ENV["reconcile_password"],
        target_new_password=ENV["target_new_password"]
    )
    p4cpm = NETHelper.get()
    assert isinstance(p4cpm, Python4CPM) # noqa: S101
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.target_account.username == ENV["target_username"] # noqa: S101
    assert p4cpm.target_account.address == ENV["target_address"] # noqa: S101
    assert p4cpm.target_account.port == ENV["target_port"] # noqa: S101
    assert p4cpm.logon_account.username == ENV["logon_username"] # noqa: S101
    assert p4cpm.reconcile_account.username == ENV["reconcile_username"] # noqa: S101
    assert p4cpm.target_account.password.get() == ENV["target_password"] # noqa: S101
    assert p4cpm.logon_account.password.get() == ENV["logon_password"] # noqa: S101
    assert p4cpm.reconcile_account.password.get() == ENV["reconcile_password"] # noqa: S101
    assert p4cpm.target_account.new_password.get() == ENV["target_new_password"] # noqa: S101
    with pytest.raises(SystemExit) as e:
        p4cpm.close_success()
        assert e.value.code == CLOSE_CODES[0] # noqa: S101
