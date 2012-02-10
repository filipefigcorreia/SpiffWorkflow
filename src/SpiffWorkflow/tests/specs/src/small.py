from SpiffWorkflow           import Workflow, Job
from SpiffWorkflow.Tasks     import *
from SpiffWorkflow.operators import *
from SpiffWorkflow.Tasks.Simple import Simple


class ASmallWorkflow(Workflow):
    def __init__(self):
        super(ASmallWorkflow, self).__init__(name = "A Small Workflow")

        multichoice = MultiChoice(self, 'multi_choice_1')
        self.start.connect(multichoice)

        a1 = Simple(self, 'task_a1')
        multichoice.connect(a1)

        a2 = Simple(self, 'task_a2')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute2'))
        multichoice.connect_if(cond, a2)

        syncmerge = Join(self, 'struct_synch_merge_1', 'multi_choice_1')
        a1.connect(syncmerge)
        a2.connect(syncmerge)

        end = Simple(self, 'End')
        syncmerge.connect(end)