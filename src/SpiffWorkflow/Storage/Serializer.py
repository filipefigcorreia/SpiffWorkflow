# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sys
from SpiffWorkflow.Task import Task

def get_class(full_class_name):
    parts = full_class_name.rsplit('.', 1)
    module_name = parts[0]
    class_name = parts[1]
    __import__(module_name)
    return getattr(sys.modules[module_name], class_name)

class Serializer(object):
    def serialize_job(self, job):
        raise NotImplementedError("You must implement the serialize_job method.")

    def deserialize_job(self, s_state):
        raise NotImplementedError("You must implement the deserialize_job method.")

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


