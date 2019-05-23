import re
import inspect

from collections import OrderedDict
from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowException

from workflows.operators import Operator


class DeclarativeOperatorsMetaclass(type):
    """Collect Operators declared on the base classes."""

    def __new__(mcs, name, bases, attrs):
        current_operators = []

        for task_id, operator_factory in list(attrs.items()):
            if isinstance(operator_factory, Operator):
                operator = operator_factory.construct(task_id)
                current_operators.append((task_id, operator))
                attrs.pop(task_id)
        attrs['declared_operators'] = OrderedDict(current_operators)

        new_class = super(DeclarativeOperatorsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        declared_operators = OrderedDict()
        for base in reversed(new_class.__mro__):
            if hasattr(base, 'declared_operators'):
                declared_operators.update(base.declared_operators)

            for attr, value in base.__dict__.items():
                if value is None and attr in declared_operators:
                    declared_operators.pop(attr)

        new_class.declared_operators = declared_operators

        if new_class.__name__ is not 'Workflow':
            new_class._create_instance()
        return new_class

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        """
        Remember the order in which operators are defined.
        """
        return OrderedDict()


class BaseWorkflow(object):
    """
    Base class provides implementation of the Workflow API. Changes should
    be made to this class, not the Workflow class itself.
    """

    def __new__(cls):
        """
        Build a DAG given a `Workflow` subclass.
        """

        dag_args = cls._create_dag_args()
        dag = DAG(**dag_args)

        # Register operator with their DAG in the order specified
        for operator in cls.declared_operators.values():
            if not operator.has_dag():
                if not inspect.isclass(operator):
                    dag.add_task(operator)
                    continue

                if not issubclass(type(operator), Operator):
                    continue

                # Hack the Airflow BaseOperator to set dag on the operator as
                # the dag setter doesn't seem to evaluate correctly
                operator._dag = dag
                operator.dag = dag

        operators = cls.declared_operators.values()

        # Set dependencies
        if len(operators) > 1:
            cls.dependencies(operators)

        # Make DAG itself accessible from the created class
        cls.DAG = dag

    @classmethod
    def __snake_case(cls, string):
        _string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', _string).lower()

    @classmethod
    def _first(cls, collection):
        """
        Return the first element from an ordered collection
        or an arbitrary element from an unordered collection.
        Raise StopIteration if the collection is empty.
        """
        return next(iter(collection))

    @classmethod
    def _create_dag_args(cls):
        """
        Create a dict of dag arguments given the Workflow metadata on the class.
        """

        metadata = {}
        if cls.__dict__.get('Meta', False):
            metadata = cls.__dict__['Meta'].__dict__
        else:
            if cls.__bases__[0].__dict__.get('Meta', False):
                parent_class_metadata = cls.__bases__[0].__dict__['Meta'].__dict__
                # TODO: Use function to do this more dynamically
                name = 'Meta'
                bases = object,
                attrs = dict(parent_class_metadata)
                setattr(cls, 'Meta', type(name, bases, attrs))

                metadata = cls.__dict__['Meta'].__dict__
            else:
                raise AirflowException('''Workflow metadata class "Meta" does not
                                   exist on this class or its direct parent.''')


        dag_init = inspect.getargspec(DAG.__init__)
        dag_args = {}
        for key, value in metadata.items():
            if key in dag_init.args:
                dag_args[key] = value

            # TODO: Raise error/warning if we skipped any user specified
            # attributes

        if not dag_args.get('start_date'):
            raise AirflowException('"start_date" not set in workflow metadata.')

        if not dag_args.get('dag_id'):
            base_name = '_' + cls.__snake_case(cls.__name__)

            start_date = dag_args['start_date']
            if not isinstance(start_date, datetime):
                raise AirflowException(
                    'Ensure the start date for your DAG is a datetime object.',
                )

            dag_args['dag_id'] = base_name + "_" + start_date.strftime(
                "%Y-%m-%dT%H-%M"
            )

        return dag_args

    @classmethod
    def _create_instance(cls):
        return cls()

    def parallelize(self, *dags):
        """
        Run two Airflow tasks in parallel.
        """
        raise NotImplemented()

    @classmethod
    def dependencies(cls, operators):
        """
        Dictate to Airflow the dependency structure for each task.

        Called only if there is more than one dependency set.
        By default, tasks execute in the order specified.
        """

        parent = cls._first(operators)
        for operator in list(operators)[1:]:
            try:
                operator.set_upstream(parent)
            except AirflowException as e:
                print('Skipping operator as it was already registered...')

            parent = operator


class Workflow(BaseWorkflow, metaclass=DeclarativeOperatorsMetaclass):
    """
    Use metaclass magic that provides the declarative syntactic sugar.

    Changes intended to be made to the Workflow API should be made to this
    class' base class preferentially instead of this class
    """
