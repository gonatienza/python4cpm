from python4cpm import Python4CPM, ReturnedPassword


p4cpm = Python4CPM()
p4cpm.target_account.set_password(ReturnedPassword.from_string("R3turnedP@ssw0rd"))
p4cpm.close_success()
