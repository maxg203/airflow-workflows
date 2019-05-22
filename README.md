# Workflows
Workflows are a cleaner way of implementing DAGs using a Django-inspired class-based syntax.

## Simple Example
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

```python
from dags import workflows
workflow_names = [
    'Test1',
    'Test2',
    'Test3',
]

for workflow in workflow_names:
    WorkflowClass = workflows.create_workflow(
        workflow,
        base=OpticalExpressWorkflow,
    )
    globals()[WorkflowClass.DAG.dag_id] = WorkflowClass.DAG
```
