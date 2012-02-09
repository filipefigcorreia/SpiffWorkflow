import sys, unittest, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from SpiffWorkflow           import Workflow, Job
from SpiffWorkflow.Tasks     import *
from SpiffWorkflow.Operators import *
from SpiffWorkflow.Task      import *
from SpiffWorkflow.Tasks.Simple import Simple
from SpiffWorkflow.Storage import DictionarySerializer

class ASmallWorkflow(Workflow):
    def __init__(self):
        super(ASmallWorkflow, self).__init__(name = "asmallworkflow")

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

class PersistSmallWorkflowTest(unittest.TestCase):
    """Runs persistency tests agains a small and easy to inspect workflowdefinition"""
    def setUp(self):
        self.wf = ASmallWorkflow()
        self.job = self._advance_to_a1(self.wf)

    def _advance_to_a1(self, wf):
        job = Job(wf)

        tasks = job.get_tasks(Task.READY)
        task_start = tasks[0]
        job.complete_task_from_id(task_start.id)

        tasks = job.get_tasks(Task.READY)
        multichoice = tasks[0]
        job.complete_task_from_id(multichoice.id)

        tasks = job.get_tasks(Task.READY)
        task_a1 = tasks[0]
        job.complete_task_from_id(task_a1.id)
        return job

    def testDictionarySerializer(self):
        """
        Tests the SelectivePickler serializer for persisting  Jobs and Tasks.
        """
        old_job = self.job
        serializer = DictionarySerializer()
        serialized_job = old_job.serialize(serializer)

        serializer = DictionarySerializer()
        new_job = Job.deserialize(serializer, serialized_job)

        before = old_job.get_dump()
        after = new_job.get_dump()
        self.assert_(before == after, 'Before:\n' + before + '\n' \
                                    + 'After:\n'  + after  + '\n')


