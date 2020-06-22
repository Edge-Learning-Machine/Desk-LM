import abc
from OutputMgr import OutputMgr

class ANN_OM(OutputMgr):
    def __init__(self, estimator):
        super().__init__()
        self.estimator = estimator

    def saveParams(self, best_estimator):
        #outdir = OutputMgr.checkCreateDSDir(self.estimator.dataset.name, self.estimator.nick)
        outdirM = OutputMgr.getOutModelDir()

        best_estimator.model.save(outdirM + f'/ann_model.h5')
        