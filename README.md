# Workflows
Workflows are a cleaner way of implementing DAGs using a Django-inspired class-based syntax.

## Simple Example
Let's create a single Airflow DAG, whose name is a camelcased version of the class name, and whose operator dependencies are in the order they are defined.

There is an option to override the default [`dependencies`](https://github.com/maxg203/airflow-workflows/blob/master/workflows.py#L165) method implementation to customise the dependency chain for your use case.

```python
import workflows


class ExampleWorkflow(workflows.Workflow):
    class Meta:
        schedule_interval = '0 9 * * *'

    do_something_useful = workflows.PythonOperator(
        python_callable=lambda **kwargs: print('something useful'),
    )
    something_else = workflows.PythonOperator(
        python_callable=lambda **kwargs: print('Something not useful'),
    )


globals()[ExampleWorkflow.DAG.dag_id] = ExampleWorkflow.DAG
```


## Dynamic DAG Example
Let's create (in this case three) DAGs, created dynamically and based on the `ExampleWorkflow` class as implemented above. In other words, they will share the same DAG metadata (so schedule in this case).

```python
import workflows

workflow_names = [
    'Test1',
    'Test2',
    'Test3',
]

for workflow in workflow_names:
    WorkflowClass = workflows.create_workflow(
        workflow,
        base=ExampleWorkflow,
    )
    globals()[WorkflowClass.DAG.dag_id] = WorkflowClass.DAG
```
