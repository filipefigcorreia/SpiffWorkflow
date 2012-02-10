import sys, unittest, os.path

from SpiffWorkflow           import Job
from SpiffWorkflow.Task      import *
from SpiffWorkflow.storage   import Serializer
from SpiffWorkflow.tests.specs.src.small import ASmallWorkflow

def get_class(full_class_name):
    parts = full_class_name.rsplit('.', 1)
    module_name = parts[0]
    class_name = parts[1]
    __import__(module_name)
    return getattr(sys.modules[module_name], class_name)

class DictionarySerializer(Serializer):
    def serialize_job(self, job):
        s_state = dict()
        s_state['attributes'] = job.attributes
        s_state['last_task'] = job.last_task.id if not job.last_task is None else None
        s_state['success'] = job.success
        s_state['task_tree'] = [self.serialize_task(task) for task in Task.Iterator(job.task_tree)]
        s_state['workflow'] = job.workflow.__class__.__module__ + '.' + job.workflow.__class__.__name__
        return s_state

    def deserialize_job(self, s_state):
        from SpiffWorkflow.Job import Job
        wf_class = get_class(s_state['workflow'])
        wf = wf_class()
        job = Job(wf)
        job.attributes = s_state['attributes']
        job.last_task = s_state['last_task']
        job.success = s_state['success']
        tasks = [self.deserialize_task(job, serialized_task) for serialized_task in s_state['task_tree']]
        job.task_tree = [task for task in tasks if task.spec.name == 'Root'][0]
        job.workflow = wf
        return job

    def serialize_task(self, task):
        s_state = dict()
        s_state['id'] = task.id
        s_state['state'] = task.state
        s_state['last_state_change'] = task.last_state_change
        s_state['attributes'] = task.attributes
        s_state['internal_attributes'] = task.internal_attributes
        return s_state

    def deserialize_task(self, job, s_state):
        task = job.get_task(s_state['id'])
        task.state = s_state['state']
        task.last_state_change = s_state['last_state_change']
        task.attributes = s_state['attributes']
        task.internal_attributes = s_state['internal_attributes']
        return task

class SerializeSmallWorkflowTest(unittest.TestCase):
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


