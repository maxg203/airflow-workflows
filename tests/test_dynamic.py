import unittest
import workflows

from datetime import datetime


class BaseTestWorkflow(workflows.Workflow):
    class Meta:
        schedule_interval = None
        start_date = datetime(2018, 10, 5)


class TestDynamic(unittest.TestCase):
    def setUp(self):
        class Meta:
            start_date = datetime(2018, 10, 30)

        operators = workflows.PythonOperator(
            task_id='test_operator',
            python_callable=lambda **kwargs: print('Hello, workflows!'),
        ),
        self.TestWorkflow = workflows.create_workflow(
            'test_workflow',
            *operators,
            workflow=workflows.Workflow,
            Meta=Meta,
        )

        self.operators = operators

    def test_dynamic_workflow_creation(self):
        workflows.create_workflow('test_workflow', workflow=BaseTestWorkflow)

    def test_workflow_class_generates_task_id_as_required(self):
        task_id = 'operator_1'
        assert self.TestWorkflow.declared_operators.get(task_id, False), \
                '`task_id` is likely not set correctly.'

    def test_workflow_class_has_operators_if_specified(self):
        task_id = 'operator_1'
        operator = self.operators[0].construct(task_id)
        operator = self.TestWorkflow.declared_operators.get(task_id, False)
        assert operator != False, "Can't find the relevant operator on the Workflow class"
        assert self.TestWorkflow.declared_operators[task_id].__class__ == \
                operator.__class__, "Incorrect operator is present on Workflow class"
