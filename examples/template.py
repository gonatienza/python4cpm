from python4cpm import Python4CPMHandler


class CredManager(Python4CPMHandler):
    """
    Accounts:
        self.target_account.username
        self.target_account.address
        self.target_account.port
        self.target_account.password.get()
        self.logon_account.username
        self.logon_account.password.get()
        self.reconcile_account.username
        self.reconcile_account.password.get()

    Logging:
        self.logger.critical("this is critical message")
        self.logger.error("this is an error message")
        self.logger.warning("this is a warning message")
        self.logger.info("this is an info message")
        self.logger.debug("this is a debug message")

    Termination signals:
        self.close_success()
        self.close_fail()
        self.close_fail(unrecoverable=True)
    """

    def verify(self):
        # TODO: add verify logic
        self.close_success()

    def logon(self):
        # TODO: add verify logic
        self.close_success()

    def change(self):
        # TODO: add verify logic
        self.close_success()

    def prereconcile(self):
        # TODO: add verify logic
        self.close_success()

    def reconcile(self):
        # TODO: add verify logic
        self.close_success()


if __name__ == "__main__":
    CredManager().run()
