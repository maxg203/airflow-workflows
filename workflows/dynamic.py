from workflows import Workflow


def create_workflow(name, *operators, **attrs):
    workflow = attrs.get('workflow')
    if not workflow:
        workflow = Workflow

    if operators:
        for index, operator in enumerate(operators):
            attrs['operator_{}'.format(index + 1)] = operator

    bases = (workflow,)
    new_workflow_class = type(name, bases, attrs)
    return new_workflow_class
