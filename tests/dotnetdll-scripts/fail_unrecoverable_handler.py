from python4cpm import Python4CPMHandler


class FailUnrecoverableHandler(Python4CPMHandler):
    def verify(self):
        self.close_fail(unrecoverable=True)

    def logon(self):
        self.close_fail(unrecoverable=True)

    def change(self):
        self.close_fail(unrecoverable=True)

    def prereconcile(self):
        self.close_fail(unrecoverable=True)

    def reconcile(self):
        self.close_fail(unrecoverable=True)


FailUnrecoverableHandler().run()
