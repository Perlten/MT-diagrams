from test_project.controller.controller import save


def add(x, y):
    save(x)
    save(y)
    return x + y