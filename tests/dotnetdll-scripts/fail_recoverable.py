from python4cpm import Python4CPM
import os


p4cpm = Python4CPM(os.path.basename(__file__))
p4cpm.close_fail(unrecoverable=False)
