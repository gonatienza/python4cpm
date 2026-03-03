from python4cpm.python4cpm import Python4CPM
from python4cpm.python4cpmhandler import Python4CPMHandler
from python4cpm.secrets import Secrets
from python4cpm.args import Args
from python4cpm.crypto import Crypto
from python4cpm.nethelper import NETHelper
from python4cpm.logger import Logger
import json
import pytest
import os


def get_args_and_secrets():
    file_dir = os.path.dirname(__file__)
    args_path = os.path.join(file_dir, "sources", "args.json")
    secrets_path = os.path.join(file_dir, "sources", "secrets.json")
    with open(args_path, "r") as f:
        args = json.load(f)
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    return args, secrets


LOGGER = Logger.get_logger(
    os.path.basename(__file__),
    Logger._LOGGING_ENABLED_VALUE,
    list(Logger._LOGGING_LEVELS.keys())[0]
)
ARGS, SECRETS = get_args_and_secrets()
LOGGING = ["yes", "YES", "bad"]
LOGGING_LEVELS = ["info", "INFO", "debug", "DEBUG", "bad"]
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


@pytest.mark.parametrize("action,logging,logging_level", ARGS_PARAMS)
def test_main(action, logging, logging_level,  monkeypatch):
    args = {Python4CPM._get_env_key(k): v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = action
    args[Python4CPM._get_env_key(Args.ARGS[6])] = logging
    args[Python4CPM._get_env_key(Args.ARGS[7])] = logging_level
    LOGGER.info(f"args -> {args}")
    secrets = {Python4CPM._get_env_key(k): v for k, v in SECRETS.items()}
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        secrets[Python4CPM._get_env_key(Secrets.SECRETS[3])] = ""
    LOGGER.info(f"secrets -> {secrets}")
    if Crypto.ENABLED:
        encrypted_secrets = {}
        for k, v in secrets.items():
            encrypted_secrets[k] = Crypto.encrypt(v)
        final_env = args | encrypted_secrets
    else:
        final_env = args | secrets
    for k, v in final_env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_main.__name__)
    for k, v in vars(p4cpm.args).items():
        LOGGER.info(f"{k} -> {v}")
    for k, v in vars(p4cpm.secrets).items():
        LOGGER.info(f"{k} -> {v.get()}")
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.username == ARGS["username"] # noqa: S101
    assert p4cpm.args.address == ARGS["address"] # noqa: S101
    assert p4cpm.args.port == ARGS["port"] # noqa: S101
    assert p4cpm.args.logon_username == ARGS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == ARGS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.secrets.password.get() == SECRETS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == SECRETS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == SECRETS["reconcile_password"] # noqa: S101
    new_password_var = f"{Python4CPM._ENV_PREFIX}{Secrets.SECRETS[3].upper()}"
    assert p4cpm.secrets.new_password.get() == secrets[new_password_var] # noqa: S101
    if logging.lower() in Logger._LOGGING_ENABLED_VALUE:
        assert p4cpm._logger # noqa: S101
        if logging_level.lower() == LOGGING_LEVELS[2]:
            assert p4cpm._logger.level == Logger._LOGGING_LEVELS[LOGGING_LEVELS[2]] # noqa: S101
        else:
            assert p4cpm._logger.level == Logger._LOGGING_LEVELS[LOGGING_LEVELS[0]] # noqa: S101
    else:
            assert p4cpm._logger is None # noqa: S101
    with pytest.raises(SystemExit) as e:
        p4cpm.close_success() # avoiding stderr output
    assert e.value.code == CLOSE_CODES[0] # noqa: S101
    with pytest.raises(SystemExit):
        GoodClass().run()
    with pytest.raises(TypeError):
        BadClassNoMethods().run()


def test_handler_bad_action(monkeypatch):
    args = {Python4CPM._get_env_key(k): v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = "nonexistent"
    args[Python4CPM._get_env_key(Args.ARGS[6])] = LOGGING[0]
    args[Python4CPM._get_env_key(Args.ARGS[7])] = LOGGING_LEVELS[0]
    LOGGER.info(f"args -> {args}")
    secrets = {Python4CPM._get_env_key(k): v for k, v in SECRETS.items()}
    encrypted_secrets = {}
    if Crypto.ENABLED:
        for k, v in secrets.items():
            encrypted_secrets[k] = Crypto.encrypt(v)
    LOGGER.info(f"secrets -> {secrets}")
    if encrypted_secrets:
        final_env = args | encrypted_secrets
    else:
        final_env = args | secrets
    for k, v in final_env.items():
        monkeypatch.setenv(k, v)
    with pytest.raises(ValueError):
        GoodClass().run()


@pytest.mark.parametrize("close", CLOSE_CODES)
def test_exit_codes(close, monkeypatch, capsys):
    args = {f"{Python4CPM._ENV_PREFIX}{k.upper()}": v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = Python4CPM.ACTION_CHANGE
    args[Python4CPM._get_env_key(Args.ARGS[6])] = LOGGING[0]
    args[Python4CPM._get_env_key(Args.ARGS[7])] = LOGGING_LEVELS[0]
    LOGGER.info(f"args -> {args}")
    secrets = {f"{Python4CPM._ENV_PREFIX}{k.upper()}": v for k, v in SECRETS.items()}
    LOGGER.info(f"secrets -> {secrets}")
    final_env = args | secrets
    for k, v in final_env.items():
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
    args = {f"{Python4CPM._ENV_PREFIX}{k.upper()}": v for k, v in ARGS.items()}
    args[Python4CPM._get_env_key(Args.ARGS[0])] = Python4CPM.ACTION_CHANGE
    args[Python4CPM._get_env_key(Args.ARGS[6])] = LOGGING[0]
    args[Python4CPM._get_env_key(Args.ARGS[7])] = LOGGING_LEVELS[0]
    LOGGER.info(f"args -> {args}")
    secrets = {f"{Python4CPM._ENV_PREFIX}{k.upper()}": v for k, v in SECRETS.items()}
    LOGGER.info(f"secrets -> {secrets}")
    final_env = args | secrets
    for k, v in final_env.items():
        monkeypatch.setenv(k, v)
    p4cpm = Python4CPM(test_on_exit_stderr.__name__)
    p4cpm._on_exit()
    captured = capsys.readouterr()
    assert captured.err != "" # noqa: S101


def test_net_helper():
    action = Python4CPM.ACTION_CHANGE
    logging = LOGGING[0]
    logging_level = LOGGING_LEVELS[2]
    NETHelper.set(
        action=action,
        address=ARGS["address"],
        username=ARGS["username"],
        port=ARGS["port"],
        logon_username=ARGS["logon_username"],
        reconcile_username=ARGS["reconcile_username"],
        logging=logging,
        logging_level=logging_level,
        password=SECRETS["password"],
        logon_password=SECRETS["logon_password"],
        reconcile_password=SECRETS["reconcile_password"],
        new_password=SECRETS["new_password"]
    )
    p4cpm = NETHelper.get()
    assert isinstance(p4cpm, Python4CPM) # noqa: S101
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.username == ARGS["username"] # noqa: S101
    assert p4cpm.args.address == ARGS["address"] # noqa: S101
    assert p4cpm.args.port == ARGS["port"] # noqa: S101
    assert p4cpm.args.logon_username == ARGS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == ARGS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.secrets.password.get() == SECRETS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == SECRETS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == SECRETS["reconcile_password"] # noqa: S101
    assert p4cpm.secrets.new_password.get() == SECRETS["new_password"] # noqa: S101
    with pytest.raises(SystemExit) as e:
        p4cpm.close_success()
        assert e.value.code == CLOSE_CODES[0] # noqa: S101
