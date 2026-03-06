from python4cpm import Python4CPMHandler
from psycopg import connect, sql


class Postgres(Python4CPMHandler):
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
        self._change(from_reconcile=True)
        self.close_success()

    def _get_creds(self, from_reconcile=False):
        if from_reconcile is False:
            username = self.target_account.username
            password = self.target_account.password.get()
        else:
            username = self.reconcile_username.username
            password = self.reconcile_account.password.get()
        return username, password


    def _verify(self, from_reconcile=False):
        username, password = self._get_creds(from_reconcile)
        try:
            with connect(
                host=self.target_account.address,
                dbname="postgres",
                user=username,
                password=password,
                autocommit=True
            ) as conn:
                with conn.cursor():
                    self.logger.info("Password verified successfully")
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            self.close_fail()

    def _change(self, from_reconcile=False):
        username, password = self._get_creds(from_reconcile)
        try:
            with connect(
                host=self.target_account.address,
                dbname="postgres",
                user=username,
                password=password,
                autocommit=True
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql.SQL("ALTER USER {} WITH PASSWORD {}").format(
                            sql.Identifier(self.target_account.username),
                            sql.Literal(self.target_account.new_password.get())
                        )
                    )
                    self.logger.info("Password changed successfully")
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            self.close_fail()

if __name__ == "__main__":
    Postgres().run()
