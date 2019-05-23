from airflow.operators.python_operator import PythonOperator as AirflowPythonOperator
from airflow.operators.bash_operator import BashOperator as AirflowBashOperator
from airflow.operators.slack_operator import (
    SlackAPIPostOperator as AirflowSlackAPIPostOperator
)
from airflow.operators import SubDagOperator as AirflowSubDagOperator
from airflow.executors.sequential_executor import SequentialExecutor


class RelaxedSubDagOperator(AirflowSubDagOperator):
    """
    Workaround Airflow SubDags requiring a parent DAG to be specified at
    subdag instantiation
    """

    def __init__(self, subdag, executor=SequentialExecutor(), *args, **kwargs):
        self.subdag = subdag
        self.executor = executor

        super(AirflowSubDagOperator, self).__init__(*args, **kwargs)


class Operator(object):
    """Operator base class."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def construct(self, task_id):
        if not self.kwargs.get('task_id'):
            self.kwargs['task_id'] = task_id

        return self.get_airflow_operator()


class PythonOperator(Operator):
    """Workflow compatible Python operator for Airflow."""

    def get_airflow_operator(self):
        return AirflowPythonOperator(*self.args, **self.kwargs)


class BashOperator(Operator):
    def get_airflow_operator(self):
        return AirflowBashOperator(*self.args, **self.kwargs)


class SlackAPIPostOperator(Operator):
    def get_airflow_operator(self):
        return AirflowSlackAPIPostOperator(*self.args, **self.kwargs)


class SubDagOperator(Operator):
    def get_airflow_operator(self):
        return RelaxedSubDagOperator(*self.args, **self.kwargs)
