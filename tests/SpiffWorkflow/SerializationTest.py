import sys, unittest, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import *
from SpiffWorkflow.operators import *
from SpiffWorkflow.Task import *
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.storage   import Serializer

class ASmallWorkflow(WorkflowSpec):
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

def get_class(full_class_name):
    parts = full_class_name.rsplit('.', 1)
    module_name = parts[0]
    class_name = parts[1]
    __import__(module_name)
    return getattr(sys.modules[module_name], class_name)

class DictionarySerializer(Serializer):
    def serialize_workflow(self, workflow):
        s_state = dict()
        s_state['attributes'] = workflow.attributes
        s_state['last_task'] = workflow.last_task.id if not workflow.last_task is None else None
        s_state['success'] = workflow.success
        s_state['task_tree'] = [self.serialize_task(task) for task in Task.Iterator(workflow.task_tree)]
        s_state['workflow'] = workflow.spec.__class__.__module__ + '.' + workflow.spec.__class__.__name__
        return s_state

    def deserialize_workflow(self, s_state):
        wf_spec_class = get_class(s_state['workflow'])
        wf_spec = wf_spec_class()
        workflow = Workflow(wf_spec)
        workflow.attributes = s_state['attributes']
        workflow.last_task = s_state['last_task']
        workflow.success = s_state['success']
        tasks = [self.deserialize_task(workflow, serialized_task) for serialized_task in s_state['task_tree']]
        workflow.task_tree = [task for task in tasks if task.task_spec.name == 'Root'][0]
        workflow.spec = wf_spec
        return workflow

    def serialize_task(self, task):
        s_state = dict()
        s_state['id'] = task.id
        s_state['state'] = task.state
        s_state['last_state_change'] = task.last_state_change
        s_state['attributes'] = task.attributes
        s_state['internal_attributes'] = task.internal_attributes
        return s_state

    def deserialize_task(self, workflow, s_state):
        task = workflow.get_task(s_state['id'])
        task.state = s_state['state']
        task.last_state_change = s_state['last_state_change']
        task.attributes = s_state['attributes']
        task.internal_attributes = s_state['internal_attributes']
        return task

class SerializeSmallWorkflowTest(unittest.TestCase):
    """Runs persistency tests agains a small and easy to inspect workflowdefinition"""
    def setUp(self):
        self.wf_spec = ASmallWorkflow()
        self.workflow = self._advance_to_a1(self.wf_spec)

    def _advance_to_a1(self, wf_spec):
        workflow = Workflow(wf_spec)

        tasks = workflow.get_tasks(Task.READY)
        task_start = tasks[0]
        workflow.complete_task_from_id(task_start.id)

        tasks = workflow.get_tasks(Task.READY)
        multichoice = tasks[0]
        workflow.complete_task_from_id(multichoice.id)

        tasks = workflow.get_tasks(Task.READY)
        task_a1 = tasks[0]
        workflow.complete_task_from_id(task_a1.id)
        return workflow

    def testDictionarySerializer(self):
        """
        Tests the SelectivePickler serializer for persisting Workflows and Tasks.
        """
        old_job = self.workflow
        serializer = DictionarySerializer()
        serialized_job = old_job.serialize(serializer)

        serializer = DictionarySerializer()
        new_job = Workflow.deserialize(serializer, serialized_job)

        before = old_job.get_dump()
        after = new_job.get_dump()
        self.assert_(before == after, 'Before:\n' + before + '\n' \
                                    + 'After:\n'  + after  + '\n')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PersistSmallWorkflowTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
