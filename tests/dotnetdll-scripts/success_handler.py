from python4cpm import Python4CPMHandler


class SuccessHandler(Python4CPMHandler):
    def verify(self):
        self.close_success()

    def logon(self):
        self.close_success()

    def change(self):
        self.close_success()

    def prereconcile(self):
        self.close_success()

    def reconcile(self):
        self.close_success()


SuccessHandler().run()
