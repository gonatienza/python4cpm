from python4cpm import Python4CPM, Secrets, Args, TPCHelper
from configparser import ConfigParser
import json
import pytest
import os
import sys


def get_prompts_and_inputs():
    file_dir = os.path.dirname(__file__)
    inputs_path = os.path.join(file_dir, "inputs.json")
    with open(inputs_path, "r") as f:
        inputs = json.load(f)
    root_dir = os.path.dirname(file_dir)
    prompts_file = os.path.join(root_dir, "src", "plugin", "Python4CPMPrompts.ini")
    _prompts = ConfigParser()
    _prompts.read(prompts_file)
    prompts = _prompts["conditions"]
    return inputs, prompts


INPUTS, PROMPTS = get_prompts_and_inputs()
ARGS = [
    "", # sys.argv[0] is ignored by argparse
    f"--{Args.ARGS[1]}={INPUTS['address']}",
    f"--{Args.ARGS[2]}={INPUTS['username']}",
    f"--{Args.ARGS[3]}={INPUTS['logon_username']}",
    f"--{Args.ARGS[4]}={INPUTS['reconcile_username']}"
]
LOGGING = ["yes", "YES", "bad"]
LOGGING_LEVELS = ["info", "debug", "DEBUG", "bad"]
ARGS_PARAMS = [
    (action, logging, logging_level)
    for logging in LOGGING
    for logging_level in LOGGING_LEVELS
    for action in Python4CPM._VALID_ACTIONS
]
INPUTS_WITHOUT_NEW_PASSWORD = [
    INPUTS[Secrets.SECRETS[0]],
    INPUTS[Secrets.SECRETS[1]],
    INPUTS[Secrets.SECRETS[2]],
    ""
]
INPUTS_WITH_NEW_PASSWORD = [
    INPUTS[Secrets.SECRETS[0]],
    INPUTS[Secrets.SECRETS[1]],
    INPUTS[Secrets.SECRETS[2]],
    INPUTS[Secrets.SECRETS[3]]
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
INPUT_PROMPTS = [
    PROMPTS["SetPasswordPrompt"],
    PROMPTS["SetLogonPasswordPrompt"],
    PROMPTS["SetReconcilePasswordPronmpt"],
    PROMPTS["SetNewPasswordPrompt"]
]
SUCCESS_PROMPT = PROMPTS["SuccessPrompt"]
FAILED_RECOVERABLE_PROMPT = PROMPTS["FailedRecoverablePrompt"]
FAILED_UNRECOVERABLE_PROMPT = PROMPTS["FailedUnrecoverablePrompt"]
CLOSE_SIGNALS = [
    Python4CPM.SUCCESS_PROMPT,
    Python4CPM.FAILED_RECOVERABLE_PROMPT,
    Python4CPM.FAILED_UNRECOVERABLE_PROMPT
]


@pytest.mark.parametrize("action,logging,logging_level", ARGS_PARAMS)
def test_main(action, logging, logging_level,  monkeypatch):
    args = ARGS + [
        f"--action={action}",
        f"--logging={logging}",
        f"--logging_level={logging_level}"
    ]
    print(f"arguments -> {args}")
    monkeypatch.setattr(sys, "argv", args)
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        inputs = INPUTS_WITHOUT_NEW_PASSWORD
    elif action in ACTIONS_WITH_NEW_PASSWORD:
        inputs = INPUTS_WITH_NEW_PASSWORD
    print(f"inputs -> {inputs}")
    iter_inputs = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(iter_inputs))
    p4cpm = Python4CPM("PyTest")
    for k, v in vars(p4cpm.args).items():
        print(f"{k} -> {v}")
    for k, v in vars(p4cpm.secrets).items():
        print(f"{k} -> {v}")
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.address == INPUTS["address"] # noqa: S101
    assert p4cpm.args.username == INPUTS["username"] # noqa: S101
    assert p4cpm.args.logon_username == INPUTS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == INPUTS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.args.logging_level == logging_level # noqa: S101
    assert p4cpm.secrets.password.get() == INPUTS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == INPUTS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == INPUTS["reconcile_password"] # noqa: S101
    assert p4cpm.secrets.new_password.get() == inputs[3] # noqa: S101
    if logging.lower() in Python4CPM._LOGGING_ENABLED_VALUE:
        assert p4cpm._logger # noqa: S101
        if logging_level.lower() == LOGGING_LEVELS[1]:
            assert p4cpm._logger.level == p4cpm._LOGGING_LEVELS[LOGGING_LEVELS[1]] # noqa: S101
        else:
            assert p4cpm._logger.level == p4cpm._LOGGING_LEVELS[LOGGING_LEVELS[0]] # noqa: S101
    else:
            assert p4cpm._logger is None # noqa: S101


def prompt_interact(prompt):
    print(prompt)
    iter_inputs = iter(INPUTS_WITH_NEW_PASSWORD)
    return next(iter_inputs)


@pytest.mark.parametrize("close", CLOSE_SIGNALS)
def test_prompts(close, monkeypatch, capsys):
    args = ARGS + ["--action=verifypass", "--logging=no"]
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setattr("builtins.input", prompt_interact)
    p4cpm = Python4CPM("PyTest")
    if close == CLOSE_SIGNALS[0]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_success()
        assert e.value.code == 0 # noqa: S101
        close_prompt = SUCCESS_PROMPT
    elif close == CLOSE_SIGNALS[1]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_fail()
        assert e.value.code == 1 # noqa: S101
        close_prompt = FAILED_RECOVERABLE_PROMPT
    elif close == CLOSE_SIGNALS[2]:
        with pytest.raises(SystemExit) as e:
            p4cpm.close_fail(unrecoverable=True)
        assert e.value.code == 1 # noqa: S101
        close_prompt = FAILED_UNRECOVERABLE_PROMPT
    prompts = INPUT_PROMPTS + [close_prompt]
    out = capsys.readouterr().out.splitlines()
    assert out == prompts # noqa: S101


def test_tpc_helper():
    action = Python4CPM.ACTION_VERIFY
    logging = LOGGING[0]
    logging_level = LOGGING_LEVELS[0]
    p4cpm = TPCHelper.run(
        action=action,
        address=INPUTS["address"],
        username=INPUTS["username"],
        logon_username=INPUTS["logon_username"],
        reconcile_username=INPUTS["reconcile_username"],
        logging=logging,
        logging_level=logging_level,
        password=INPUTS["password"],
        logon_password=INPUTS["logon_password"],
        reconcile_password=INPUTS["reconcile_password"],
        new_password=INPUTS["new_password"]
    )
    assert isinstance(p4cpm, Python4CPM) # noqa: S101
    assert p4cpm.args.action == action # noqa: S101
    assert p4cpm.args.address == INPUTS["address"] # noqa: S101
    assert p4cpm.args.username == INPUTS["username"] # noqa: S101
    assert p4cpm.args.logon_username == INPUTS["logon_username"] # noqa: S101
    assert p4cpm.args.reconcile_username == INPUTS["reconcile_username"] # noqa: S101
    assert p4cpm.args.logging == logging # noqa: S101
    assert p4cpm.secrets.password.get() == INPUTS["password"] # noqa: S101
    assert p4cpm.secrets.logon_password.get() == INPUTS["logon_password"] # noqa: S101
    assert p4cpm.secrets.reconcile_password.get() == INPUTS["reconcile_password"] # noqa: S101
    assert p4cpm.secrets.new_password.get() == INPUTS["new_password"] # noqa: S101
