from python4cpm import Python4CPMHandler
import ssl
import urllib.request
import urllib.parse
import http.cookiejar as cookiejar
import json


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.log_info(f"NoRedirectHandler: ignoring redirect -> {newurl}")
        return None


class SimpleAuth(Python4CPMHandler):
    ROOT_URL_FORMAT = "https://{}:{}"
    TOKEN_URL_FORMAT = "https://{}:{}/token"  # noqa S105
    VERIFY_URL_FORMAT = "https://{}:{}/verify"
    CHANGE_URL_FORMAT = "https://{}:{}/change"
    RECONCILE_URL_FORMAT = "https://{}:{}/reconcile"
    USE_COOKIE = False

    def __init__(self):
        super().__init__()
        self._opener = self._get_opener()

    def verify(self):
        self._verify()
        self.close_success()

    def logon(self):
        self.close_success()

    def change(self):
        self._change()
        self.close_success()

    def prereconcile(self):
        self._verify(from_reconcile=True)
        self.close_success()

    def reconcile(self):
        self._reconcile()
        self.close_success()

    @staticmethod
    def _get_opener():
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        cookie_jar = cookiejar.CookieJar()
        return urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookie_jar),
            urllib.request.HTTPSHandler(context=ssl_ctx),
            NoRedirectHandler()
        )


    def _get_payload(self, from_reconcile):
        if not from_reconcile:
            username = self.args.username
            password = self.secrets.password.get()
        else:
            username = self.args.reconcile_username
            password = self.secrets.reconcile_password.get()
        return {
            "username": username,
            "password": password
        }


    def _set_cookie(self, from_reconcile=False):
        payload = self._get_payload(from_reconcile)
        data = urllib.parse.urlencode(payload).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        method = "POST"
        req = urllib.request.Request( # noqa S310
            self.ROOT_URL_FORMAT.format(self.args.address, self.args.port),
            data=data,
            headers=headers,
            method=method
        )
        try:
            with self._opener.open(req, timeout=10) as res:
                self.log_info(f"_set_cookie: code -> {res.code}")
                pass
        except urllib.error.HTTPError as e:
            inner_message = f"code -> {e.code}"
            message = f"_set_cookie: {inner_message}"
            if e.code != 302:
                self.log_error(message)
                raise Exception(inner_message)
            self.log_info(message)
        self.log_info("_set_cookie: cookie set")


    def _get_auth_header(self, from_reconcile=False):
        payload = self._get_payload(from_reconcile)
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        method = "POST"
        req = urllib.request.Request( # noqa S310
            self.TOKEN_URL_FORMAT.format(self.args.address, self.args.port),
            data=data,
            headers=headers,
            method=method
        )
        with self._opener.open(req, timeout=10) as _res:
            res = json.loads(_res.read().decode())
        self.log_info("get_auth_headaer: got token")
        token = res["token"]
        return {"Authorization": f"Bearer {token}"}


    def _verify(self, from_reconcile=False):
        try:
            payload = {}
            data = json.dumps(payload).encode()
            headers = {"Content-Type": "application/json"}
            method = "POST"
            if self.USE_COOKIE:
                self._set_cookie(from_reconcile)
            else:
                auth_header = self._get_auth_header(from_reconcile)
                headers.update(auth_header)
            req = urllib.request.Request( # noqa S310
                self.VERIFY_URL_FORMAT.format(self.args.address, self.args.port),
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.log_info(f"verify: {res.decode()}")
        except Exception as e:
            self.log_error(f"{type(e).__name__}: {e}")
            self.close_fail()


    def _change(self):
        try:
            payload = {"new_password": self.secrets.new_password.get()}
            data = json.dumps(payload).encode()
            headers = {"Content-Type": "application/json"}
            method = "POST"
            if self.USE_COOKIE:
                self._set_cookie()
            else:
                auth_header = self._get_auth_header()
                headers.update(auth_header)
            req = urllib.request.Request( # noqa S310
                self.CHANGE_URL_FORMAT.format(self.args.address, self.args.port),
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.log_info(f"change: {res.decode()}")
        except Exception as e:
            self.log_error(f"{type(e).__name__}: {e}")
            self.close_fail()


    def _reconcile(self):
        try:
            payload = {
                "username": self.args.username,
                "new_password": self.secrets.new_password.get()
            }
            data = json.dumps(payload).encode()
            headers = {"Content-Type": "application/json"}
            method = "POST"
            if self.USE_COOKIE:
                self._set_cookie(from_reconcile=True)
            else:
                auth_header = self._get_auth_header(from_reconcile=True)
                headers.update(auth_header)
            req = urllib.request.Request( # noqa S310
                self.RECONCILE_URL_FORMAT.format(self.args.address, self.args.port),
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.log_info(f"reconcile: {res.decode()}")
        except Exception as e:
            self.log_error(f"{type(e).__name__}: {e}")
            self.close_fail()

if __name__ == "__main__":
    SimpleAuth().run()
