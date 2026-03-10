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


def encrypt_env_keys(env):
    if Crypto.ENABLED:
        env_keys = (
            TargetAccount.get_key(TargetAccount.PROPS.password),
            LogonAccount.get_key(LogonAccount.PROPS.password),
            ReconcileAccount.get_key(ReconcileAccount.PROPS.password),
            TargetAccount.get_key(TargetAccount.PROPS.new_password)
        )
        for k in env_keys:
            env[k] = Crypto.encrypt(env[k])


@pytest.mark.parametrize("action,logging_level", ARGS_PARAMS)
def test_main(action, logging_level,  monkeypatch):
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = action
    env[Args.get_key(Args.PROPS.logging_level)] = logging_level
    encrypt_env_keys(env)
    if action not in ACTIONS_WITH_NEW_PASSWORD:
        del env[TargetAccount.get_key(TargetAccount.PROPS.new_password)]
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
    assert p4cpm.target_account.username == ENV["PYTHON4CPM_TARGET_USERNAME"] # noqa: S101
    assert p4cpm.target_account.address == ENV["PYTHON4CPM_TARGET_ADDRESS"] # noqa: S101
    assert p4cpm.target_account.port == ENV["PYTHON4CPM_TARGET_PORT"] # noqa: S101
    assert p4cpm.logon_account.username == ENV["PYTHON4CPM_LOGON_USERNAME"] # noqa: S101
    assert p4cpm.reconcile_account.username == ENV["PYTHON4CPM_RECONCILE_USERNAME"] # noqa: S101
    assert p4cpm.target_account.password.get() == ENV["PYTHON4CPM_TARGET_PASSWORD"] # noqa: S101
    assert p4cpm.logon_account.password.get() == ENV["PYTHON4CPM_LOGON_PASSWORD"] # noqa: S101
    assert p4cpm.reconcile_account.password.get() == ENV["PYTHON4CPM_RECONCILE_PASSWORD"] # noqa: S101 E501
    if action not in ACTIONS_WITH_NEW_PASSWORD:
        assert p4cpm.target_account.new_password is None # noqa: S101
    else:
        assert p4cpm.target_account.new_password.get() == ENV["PYTHON4CPM_TARGET_NEW_PASSWORD"] # noqa: S101 E501
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


def test_no_logon_account(monkeypatch):
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = Python4CPM.ACTION_CHANGE
    env[Args.get_key(Args.PROPS.logging_level)] = LOGGING_LEVELS[1]
    encrypt_env_keys(env)
    del env[LogonAccount.get_key(LogonAccount.PROPS.username)]
    del env[LogonAccount.get_key(LogonAccount.PROPS.password)]
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_no_logon_account.__name__)
    assert p4cpm.logon_account is None # noqa: S101


def test_no_reconcile_account(monkeypatch):
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = Python4CPM.ACTION_CHANGE
    env[Args.get_key(Args.PROPS.logging_level)] = LOGGING_LEVELS[1]
    encrypt_env_keys(env)
    del env[ReconcileAccount.get_key(ReconcileAccount.PROPS.username)]
    del env[ReconcileAccount.get_key(ReconcileAccount.PROPS.password)]
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_no_reconcile_account.__name__)
    assert p4cpm.reconcile_account is None # noqa: S101


def test_handler_bad_action(monkeypatch):
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = "nonexistent"
    env[Args.get_key(Args.PROPS.logging_level)] = LOGGING_LEVELS[1]
    encrypt_env_keys(env)
    LOGGER.info(f"env -> {env}")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    with pytest.raises(ValueError):
        GoodClass().run()


@pytest.mark.parametrize("close", CLOSE_CODES)
def test_exit_codes(close, monkeypatch, capsys):
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = Python4CPM.ACTION_CHANGE
    env[Args.get_key(Args.PROPS.logging_level)] = LOGGING_LEVELS[1]
    encrypt_env_keys(env)
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
    env = ENV.copy()
    env[Args.get_key(Args.PROPS.action)] = Python4CPM.ACTION_CHANGE
    env[Args.get_key(Args.PROPS.logging_level)] = LOGGING_LEVELS[1]
    encrypt_env_keys(env)
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
        target_address=ENV["PYTHON4CPM_TARGET_ADDRESS"],
        target_username=ENV["PYTHON4CPM_TARGET_USERNAME"],
        target_port=ENV["PYTHON4CPM_TARGET_PORT"],
        logon_username=ENV["PYTHON4CPM_LOGON_USERNAME"],
        reconcile_username=ENV["PYTHON4CPM_RECONCILE_USERNAME"],
        logging_level=logging_level,
        target_password=ENV["PYTHON4CPM_TARGET_PASSWORD"],
        logon_password=ENV["PYTHON4CPM_LOGON_PASSWORD"],
        reconcile_password=ENV["PYTHON4CPM_RECONCILE_PASSWORD"],
        target_new_password=ENV["PYTHON4CPM_TARGET_NEW_PASSWORD"]
    )
    p4cpm = NETHelper.get()
    assert isinstance(p4cpm, Python4CPM) # noqa: S101
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.target_account.username == ENV["PYTHON4CPM_TARGET_USERNAME"] # noqa: S101
    assert p4cpm.target_account.address == ENV["PYTHON4CPM_TARGET_ADDRESS"] # noqa: S101
    assert p4cpm.target_account.port == ENV["PYTHON4CPM_TARGET_PORT"] # noqa: S101
    assert p4cpm.logon_account.username == ENV["PYTHON4CPM_LOGON_USERNAME"] # noqa: S101
    assert p4cpm.reconcile_account.username == ENV["PYTHON4CPM_RECONCILE_USERNAME"] # noqa: S101
    assert p4cpm.target_account.password.get() == ENV["PYTHON4CPM_TARGET_PASSWORD"] # noqa: S101
    assert p4cpm.logon_account.password.get() == ENV["PYTHON4CPM_LOGON_PASSWORD"] # noqa: S101
    assert p4cpm.reconcile_account.password.get() == ENV["PYTHON4CPM_RECONCILE_PASSWORD"] # noqa: S101 E501
    assert p4cpm.target_account.new_password.get() == ENV["PYTHON4CPM_TARGET_NEW_PASSWORD"] # noqa: S101 E501
    with pytest.raises(SystemExit) as e:
        p4cpm.close_success()
        assert e.value.code == CLOSE_CODES[0] # noqa: S101
