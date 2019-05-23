import unittest

from airflow.operators.python_operator import PythonOperator as AirflowPythonOperator
from airflow.operators.bash_operator import BashOperator as AirflowBashOperator
from airflow.operators.slack_operator import (
    SlackAPIPostOperator as AirflowSlackAPIPostOperator
)

from workflows.operators import (
    Operator,
    PythonOperator,
    BashOperator,
    SlackAPIPostOperator,
)


class TestOperator(unittest.TestCase):

    def test_operator_construction_returns_expected_object(self):
        assert isinstance(Operator(), Operator)

    def test_python_operator_has_task_id_when_constructed(self):
        operator = PythonOperator(
            task_id='my_task_id',
            python_callable=lambda **kwargs: print("I'm an operator!"),
        )
        assert operator.kwargs.get('task_id', False)

        python_operator = operator.construct('my_explicit_task_id')
        assert isinstance(python_operator, AirflowPythonOperator)

    def test_bash_operator_has_task_id_when_constructed(self):
        operator = BashOperator(
            task_id='my_task_id',
            bash_command=lambda **kwargs: print("I'm an operator!"),
        )
        assert operator.kwargs.get('task_id', False)

        bash_operator = operator.construct('my_explicit_task_id')
        assert isinstance(bash_operator, AirflowBashOperator)

    def test_slack_operator_has_task_id_when_constructed(self):
        operator = SlackAPIPostOperator(task_id='my_task_id')
        assert operator.kwargs.get('task_id', False)

        slack_operator = operator.construct('my_explicit_task_id')
        assert isinstance(slack_operator, AirflowSlackAPIPostOperator)
