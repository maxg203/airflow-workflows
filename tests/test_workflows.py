import re
import inspect
import unittest
import workflows

from collections import OrderedDict
from datetime import datetime

from airflow import DAG
from airflow.models import BaseOperator


def python_callable(**kwargs):
    pass


class ExampleWorkflow(workflows.Workflow):
    do_something_useful = workflows.PythonOperator(
        python_callable=python_callable,
    )
    something_else = workflows.PythonOperator(
        python_callable=python_callable,
    )

    class Meta:
        schedule_interval = '0 9 * * *'
        start_date = datetime(2018, 10, 5)


class TestExampleWorkflow(unittest.TestCase):
    """
    Intended to test the metaclass magic in the Workflows abstraction, not
    the example class itself.
    """

    def test_dag_is_accessible(self):
        assert hasattr(ExampleWorkflow, 'DAG')

    def test_expected_dag_is_dag(self):
        assert isinstance(ExampleWorkflow.DAG, DAG)

    def test_operators_are_accessible(self):
        assert hasattr(ExampleWorkflow, 'declared_operators')

    def test_operators_are_ordered_collection(self):
        assert isinstance(ExampleWorkflow.declared_operators, OrderedDict)

    def test_operator_extends_correct_superclass(self):
        assert isinstance(
            ExampleWorkflow.declared_operators['do_something_useful'],
            BaseOperator,
        )

    def test_meta_class_is_present(self):
        assert ExampleWorkflow.__dict__.get('Meta', False)

    def test_meta_class_is_a_class(self):
        assert inspect.isclass(ExampleWorkflow.__dict__['Meta'])

    def test_first_operator_specified_is_first_one_in_class_definition(self):
        first_operator = ExampleWorkflow._first(
            ExampleWorkflow.declared_operators.keys(),
        )
        assert first_operator == 'do_something_useful'

    def test_class_name_is_snake_cased_in_dag_id(self):
        assert re.match('^_example_workflow*', ExampleWorkflow.DAG.dag_id)


def load_subdag(parent_dag_name, child_dag_name, args):
    subdag = DAG(
        dag_id='{}.{}'.format(parent_dag_name, child_dag_name),
        start_date=datetime(2018, 10, 30),
        default_args=args,
    )

    with subdag:
        workflows.PythonOperator(
            task_id='do_something_useful',
            python_callable=python_callable,
        )
        workflows.PythonOperator(
            task_id='something_else',
            python_callable=python_callable,
        )

    return subdag


class InheritedMetaWorkflow(ExampleWorkflow):
    example_operators = workflows.SubDagOperator(
        task_id='example_python_operators',
        subdag=load_subdag('parent', 'child', {}),
        default_args={'start_date': datetime(2018, 10, 30)},
    )


class TestWorkflowMetaInheritence(unittest.TestCase):
    def test_all_workflow_metadata_is_attributed_correctly(self):
        assert ExampleWorkflow.__dict__['Meta'].__dict__ == \
                InheritedMetaWorkflow.__dict__['Meta'].__dict__

    def test_workflow_meta_class_is_recreated_not_duplicated(self):
        example_meta_class = ExampleWorkflow.__dict__['Meta']
        inherited_meta_class = InheritedMetaWorkflow.__dict__['Meta']

        assert example_meta_class != inherited_meta_class
