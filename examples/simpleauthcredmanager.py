from python4cpm import Python4CPMHandler
import ssl
import urllib.request
import urllib.parse
import http.cookiejar as cookiejar
import json


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.logger.info(f"NoRedirectHandler: ignoring redirect -> {newurl}")
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
            username = self.target_account.username
            password = self.target_account.password.get()
        else:
            username = self.reconcile_account.username
            password = self.reconcile_account.password.get()
        return {
            "username": username,
            "password": password
        }


    def _set_cookie(self, from_reconcile=False):
        payload = self._get_payload(from_reconcile)
        data = urllib.parse.urlencode(payload).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        method = "POST"
        url = self.ROOT_URL_FORMAT.format(
            self.target_account.address,
            self.target_account.port
        )
        req = urllib.request.Request( # noqa S310
            url,
            data=data,
            headers=headers,
            method=method
        )
        try:
            with self._opener.open(req, timeout=10) as res:
                self.logger.info(f"code -> {res.code}")
                pass
        except urllib.error.HTTPError as e:
            message = f"code -> {e.code}"
            if e.code != 302:
                self.logger.error(message)
                raise Exception(message)
            self.logger.info(message)
        self.logger.info("cookie set")


    def _get_auth_header(self, from_reconcile=False):
        payload = self._get_payload(from_reconcile)
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        method = "POST"
        url = self.TOKEN_URL_FORMAT.format(
            self.target_account.address,
            self.target_account.port
        )
        req = urllib.request.Request( # noqa S310
            url,
            data=data,
            headers=headers,
            method=method
        )
        with self._opener.open(req, timeout=10) as _res:
            res = json.loads(_res.read().decode())
        self.logger.info("got token")
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
            url = self.VERIFY_URL_FORMAT.format(
                self.target_account.address,
                self.target_account.port
            )
            req = urllib.request.Request( # noqa S310
                url,
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.logger.info(f"{res.decode()}")
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
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
            url = self.CHANGE_URL_FORMAT.format(
                self.target_account.address,
                self.target_account.port
            )
            req = urllib.request.Request( # noqa S310
                url,
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.logger.info(res.decode())
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            self.close_fail()


    def _reconcile(self):
        try:
            payload = {
                "username": self.target_account.username,
                "new_password": self.target_account.new_password.get()
            }
            data = json.dumps(payload).encode()
            headers = {"Content-Type": "application/json"}
            method = "POST"
            if self.USE_COOKIE:
                self._set_cookie(from_reconcile=True)
            else:
                auth_header = self._get_auth_header(from_reconcile=True)
                headers.update(auth_header)
            url = self.RECONCILE_URL_FORMAT.format(
                self.target_account.address,
                self.target_account.port
            )
            req = urllib.request.Request( # noqa S310
                url,
                data=data,
                headers=headers,
                method=method
            )
            with self._opener.open(req, timeout=10) as _res:
                res = _res.read()
            self.logger.info(res.decode())
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            self.close_fail()

if __name__ == "__main__":
    SimpleAuth().run()
