from python4cpm.python4cpm import Python4CPM
from python4cpm.secrets import Secrets
from python4cpm.args import Args
from python4cpm.crypto import Crypto
from python4cpm.nethelper import NETHelper
from python4cpm.logger import _LOGGING_ENABLED_VALUE, _LOGGING_LEVELS
import json
import pytest
import os


def get_args_and_secrets():
    file_dir = os.path.dirname(__file__)
    args_path = os.path.join(file_dir, "env", "args.json")
    secrets_path = os.path.join(file_dir, "env", "secrets.json")
    with open(args_path, "r") as f:
        args = json.load(f)
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    return args, secrets


ARGS, SECRETS = get_args_and_secrets()
LOGGING = ["yes", "YES", "bad"]
LOGGING_LEVELS = ["info", "debug", "DEBUG", "bad"]
ARGS_PARAMS = [
    (action, logging, logging_level)
    for logging in LOGGING
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


@pytest.mark.parametrize("action,logging,logging_level", ARGS_PARAMS)
def test_main(action, logging, logging_level,  monkeypatch):
    args = {Python4CPM._get_env_key(k): v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = action
    args[Python4CPM._get_env_key(Args.ARGS[5])] = logging
    args[Python4CPM._get_env_key(Args.ARGS[6])] = logging_level
    print(f"args -> {args}")
    secrets = {Python4CPM._get_env_key(k): v for k, v in SECRETS.items()}
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        secrets[Python4CPM._get_env_key(Secrets.SECRETS[3])] = ""
    encrypted_secrets = {}
    if Crypto.ENABLED:
        for k, v in secrets.items():
            encrypted_secrets[k] = Crypto.encrypt(v)
    print(f"secrets -> {secrets}")
    if encrypted_secrets:
        final_env = args | encrypted_secrets
    else:
        final_env = args | secrets
    for k, v in final_env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM("PyTest")
    for k, v in vars(p4cpm.args).items():
        print(f"{k} -> {v}")
    for k, v in vars(p4cpm.secrets).items():
        print(f"{k} -> {v}")
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.address == ARGS["address"] # noqa: S101
    assert p4cpm.args.username == ARGS["username"] # noqa: S101
    assert p4cpm.args.logon_username == ARGS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == ARGS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.secrets.password.get() == SECRETS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == SECRETS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == SECRETS["reconcile_password"] # noqa: S101
    assert p4cpm.secrets.new_password.get() == secrets["PYTHON4CPM_NEW_PASSWORD"] # noqa: S101
    if logging.lower() in _LOGGING_ENABLED_VALUE:
        assert p4cpm._logger # noqa: S101
        if logging_level.lower() == LOGGING_LEVELS[1]:
            assert p4cpm._logger.level == _LOGGING_LEVELS[LOGGING_LEVELS[1]] # noqa: S101
        else:
            assert p4cpm._logger.level == _LOGGING_LEVELS[LOGGING_LEVELS[0]] # noqa: S101
    else:
            assert p4cpm._logger is None # noqa: S101


@pytest.mark.parametrize("close", CLOSE_CODES)
def test_exit_codes(close, monkeypatch):
    args = {f"PYTHON4CPM_{k.upper()}": v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = Python4CPM.ACTION_VERIFY
    args[Python4CPM._get_env_key(Args.ARGS[5])] = LOGGING[0]
    args[Python4CPM._get_env_key(Args.ARGS[6])] = LOGGING_LEVELS[0]
    print(f"args -> {args}")
    secrets = {f"PYTHON4CPM_{k.upper()}": v for k, v in SECRETS.items()}
    print(f"secrets -> {secrets}")
    final_env = args | secrets
    for k, v in final_env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM("PyTest")
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


def test_net_helper():
    action = Python4CPM.ACTION_VERIFY
    logging = LOGGING[0]
    logging_level = LOGGING_LEVELS[0]
    p4cpm = NETHelper.run(
        action=action,
        address=ARGS["address"],
        username=ARGS["username"],
        logon_username=ARGS["logon_username"],
        reconcile_username=ARGS["reconcile_username"],
        logging=logging,
        logging_level=logging_level,
        password=SECRETS["password"],
        logon_password=SECRETS["logon_password"],
        reconcile_password=SECRETS["reconcile_password"],
        new_password=SECRETS["new_password"]
    )
    assert isinstance(p4cpm, Python4CPM) # noqa: S101
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.address == ARGS["address"] # noqa: S101
    assert p4cpm.args.username == ARGS["username"] # noqa: S101
    assert p4cpm.args.logon_username == ARGS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == ARGS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.secrets.password.get() == SECRETS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == SECRETS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == SECRETS["reconcile_password"] # noqa: S101
    assert p4cpm.secrets.new_password.get() == SECRETS["new_password"] # noqa: S101
