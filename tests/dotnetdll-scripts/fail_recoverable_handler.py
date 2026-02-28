from python4cpm import Python4CPMHandler


class FailRecoverableHandler(Python4CPMHandler):
    def verify(self):
        self.close_fail()

    def logon(self):
        self.close_fail()

    def change(self):
        self.close_fail()

    def prereconcile(self):
        self.close_fail()

    def reconcile(self):
        self.close_fail()


FailRecoverableHandler()
