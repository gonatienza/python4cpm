# ruff: noqa S101

from python4cpm import Python4CPM
from python4cpm.python4cpm import Secrets, Args
import json
import pytest
import os
import sys


file_dir = os.path.dirname(__file__)
inputs_path = os.path.join(file_dir, "inputs", "inputs.json")
with open(inputs_path, "r") as f:
    INPUTS = json.load(f)

ARGS = [
    "", # sys.argv[0] is ignored y argparse
    f"--{Args.ARGS[1]}={INPUTS['address']}",
    f"--{Args.ARGS[2]}={INPUTS['username']}",
    f"--{Args.ARGS[3]}={INPUTS['logon_username']}",
    f"--{Args.ARGS[4]}={INPUTS['reconcile_username']}"
]
PARAMS = [
    (action, logging)
    for logging in ["yes", "no"]
    for action in Python4CPM._VALID_ACTIONS
]
INPUTS_VERIFY_PRERECONCILE = [
    INPUTS[Secrets.SECRETS[0]],
    INPUTS[Secrets.SECRETS[1]],
    INPUTS[Secrets.SECRETS[2]],
    ""
]
INPUTS_CHANGE_RECONCILE = [
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


@pytest.mark.parametrize("action,logging", PARAMS)
def test_python4cpm(action, logging, monkeypatch):
    args = ARGS + [f"--action={action}", f"--logging={logging}"]
    monkeypatch.setattr(sys, "argv", args)
    print(f"arguments -> {sys.argv}")
    if action in ACTIONS_WITHOUT_NEW_PASSWORD:
        inputs = iter(INPUTS_VERIFY_PRERECONCILE)
        print(f"inputs -> {INPUTS_VERIFY_PRERECONCILE}")
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        p4cpm = Python4CPM("PyTest")
        assert p4cpm.secrets.new_password == ""
    elif action in ACTIONS_WITH_NEW_PASSWORD:
        inputs = iter(INPUTS_CHANGE_RECONCILE)
        print(f"inputs -> {INPUTS_CHANGE_RECONCILE}")
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        p4cpm = Python4CPM("PyTest")
        assert p4cpm.secrets.new_password == INPUTS["new_password"]
    assert p4cpm.args.action == action
    assert p4cpm.args.address == INPUTS["address"]
    assert p4cpm.args.username == INPUTS["username"]
    assert p4cpm.args.logon_username == INPUTS["logon_username"]
    assert p4cpm.args.reconcile_username == INPUTS["reconcile_username"]
    assert p4cpm.secrets.password == INPUTS["password"]
    assert p4cpm.secrets.logon_password == INPUTS["logon_password"]
    assert p4cpm.secrets.reconcile_password == INPUTS["reconcile_password"]
