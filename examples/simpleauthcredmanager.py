import ssl
import urllib.request
import urllib.parse
import http.cookiejar as cookiejar
import json
from python4cpm import Python4CPM


P4CPM = Python4CPM("SimpleAuth")


ROOT_URL_FORMAT = "https://{}:8443"
TOKEN_URL_FORMAT = "https://{}:8443/token"  # noqa S105
VERIFY_URL_FORMAT = "https://{}:8443/verify"
CHANGE_URL_FORMAT = "https://{}:8443/change"
RECONCILE_URL_FORMAT = "https://{}:8443/reconcile"
USE_COOKIE = False


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        P4CPM.log_info(f"NoRedirectHandler: ignoring redirect -> {newurl}")
        return None


def get_opener():
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    cookie_jar = cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPSHandler(context=ssl_ctx),
        NoRedirectHandler()
    )


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


def set_cookie(opener, from_reconcile=False):
    payload = _get_payload(from_reconcile)
    data = urllib.parse.urlencode(payload).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    method = "POST"
    req = urllib.request.Request( # noqa S310
        ROOT_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    try:
        with opener.open(req, timeout=10) as res:
            P4CPM.log_info(f"set_cookie: code -> {res.code}")
            pass
    except urllib.error.HTTPError as e:
        inner_message = f"code -> {e.code}"
        message = f"set_cookie: {inner_message}"
        if e.code != 302:
            P4CPM.log_error(message)
            raise Exception(inner_message)
        P4CPM.log_info(message)
    P4CPM.log_info("set_cookie: cookie set")


def get_auth_header(opener, from_reconcile=False):
    payload = _get_payload(from_reconcile)
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    req = urllib.request.Request( # noqa S310
        TOKEN_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with opener.open(req, timeout=10) as _res:
        res = json.loads(_res.read().decode())
    P4CPM.log_info("get_auth_headaer: got token")
    token = res["token"]
    return {"Authorization": f"Bearer {token}"}


def verify(opener, from_reconcile=False):
    payload = {}
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    if USE_COOKIE:
        set_cookie(opener, from_reconcile)
    else:
        auth_header = get_auth_header(opener, from_reconcile)
        headers.update(auth_header)
    req = urllib.request.Request( # noqa S310
        VERIFY_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with opener.open(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"verify: {res.decode()}")


def change(opener):
    payload = {"new_password": P4CPM.secrets.new_password.get()}
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    if USE_COOKIE:
        set_cookie(opener)
    else:
        auth_header = get_auth_header(opener)
        headers.update(auth_header)
    req = urllib.request.Request( # noqa S310
        CHANGE_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with opener.open(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"change: {res.decode()}")


def reconcile(opener):
    payload = {
        "username": P4CPM.args.username,
        "new_password": P4CPM.secrets.new_password.get()
    }
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    method = "POST"
    if USE_COOKIE:
        set_cookie(opener, from_reconcile=True)
    else:
        auth_header = get_auth_header(opener, from_reconcile=True)
        headers.update(auth_header)
    req = urllib.request.Request( # noqa S310
        RECONCILE_URL_FORMAT.format(P4CPM.args.address),
        data=data,
        headers=headers,
        method=method
    )
    with opener.open(req, timeout=10) as _res:
        res = _res.read()
    P4CPM.log_info(f"reconcile: {res.decode()}")


def main():
    try:
        opener = get_opener()
        action = P4CPM.args.action
        if action == Python4CPM.ACTION_VERIFY:
            verify(opener)
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_LOGON:
            verify(opener)
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_CHANGE:
            change(opener)
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_PRERECONCILE:
            verify(opener, from_reconcile=True)
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_RECONCILE:
            reconcile(opener)
            P4CPM.close_success()
        else:
            P4CPM.log_error(f"main: invalid action: '{action}'")
            P4CPM.close_fail()
    except Exception as e:
        P4CPM.log_error(f"{type(e).__name__}: {e}")
        P4CPM.close_fail()


if __name__ == "__main__":
    main()
