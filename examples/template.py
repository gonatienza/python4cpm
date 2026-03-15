from python4cpm import Python4CPMHandler


class CredManager(Python4CPMHandler):
    """
    Properties:
        target_account (TargetAccount): Account being managed.
            .username (str): Account username.
            .address (str): Target address.
            .port (str): Target port.
            .password (Secret): Current password. Call .get() to retrieve value.
            .new_password (Secret): Replacement password. Call .get() to retrieve value.

        logon_account (LogonAccount): Linked Logon Account.
            .username (str): Account username.
            .password (Secret): Logon password. Call .get() to retrieve value.

        reconcile_account (ReconcileAccount): Linked Reconcile Account.
            .username (str): Account username.
            .password (Secret): Reconcile password. Call .get() to retrieve value.

        logger (logging.Logger): Logger instance.

    Methods:
        close_success(): Signal successful completion and terminate.
        close_fail(): Signal failed completion and terminate.
    """

    def verify(self):
        # TODO: add verify logic
        self.close_success()

    def logon(self):
        # TODO: add logon logic
        self.close_success()

    def change(self):
        # TODO: add change logic
        self.close_success()

    def prereconcile(self):
        # TODO: add prereconcile logic
        self.close_success()

    def reconcile(self):
        # TODO: add reconcile logic
        self.close_success()


if __name__ == "__main__":
    CredManager().run()
