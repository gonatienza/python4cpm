# ruff: noqa S105, S310

from urllib.request import Request, urlopen
import json
from python4cpm import Python4CPM


TOKEN_URL_FORMAT = "https://{}:8443/token"
VERIFY_URL_FORMAT = "https://{}:8443/verify"
CHANGE_URL_FORMAT = "https://{}:8443/change"
RECONCILE_URL_FORMAT = "https://{}:8443/reconcile"


P4CPM = Python4CPM("MyApp")


def _get_payload(from_reconcile):
    if not from_reconcile:
        username = P4CPM.args.username
        password = P4CPM.secrets.password.get()
    else:
        username = P4CPM.args.reconcile_username
        password = P4CPM.secrets.reconcile_password.get()
    return {
        "username": username,
        "password": password
    }


def get_auth_header(from_reconcile=False):
    payload = _get_payload(from_reconcile)
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    req = Request(
        TOKEN_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with urlopen(req, timeout=10) as _res:
        res = json.loads(_res.read().decode())
    P4CPM.log_info("get_auth_headaer: got token")
    token = res["token"]
    return {"Authorization": f"Bearer {token}"}


def verify():
    payload = {}
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    auth_header = get_auth_header()
    headers.update(auth_header)
    req = Request(
        VERIFY_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with urlopen(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"verify: {res.decode()}")


def change():
    payload = {"new_password": P4CPM.secrets.new_password.get()}
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    auth_header = get_auth_header()
    headers.update(auth_header)
    req = Request(
        CHANGE_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with urlopen(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"change: {res.decode()}")


def reconcile():
    payload = {
        "username": P4CPM.args.username,
        "new_password": P4CPM.secrets.new_password.get()
    }
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    auth_header = get_auth_header(from_reconcile=True)
    headers.update(auth_header)
    req = Request(
        RECONCILE_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with urlopen(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"reconcile: {res.decode()}")


def main():
    try:
        action = P4CPM.args.action
        if action == Python4CPM.ACTION_VERIFY:
            verify()
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_LOGON:
            pass
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_CHANGE:
            change()
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_PRERECONCILE:
            pass
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_RECONCILE:
            reconcile()
            P4CPM.close_success()
        else:
            P4CPM.log_error(f"main: invalid action: '{action}'")
            P4CPM.close_fail()
    except Exception as e:
        P4CPM.log_error(f"{type(e).__name__}: {e}")
        P4CPM.close_fail()


if __name__ == "__main__":
    main()
