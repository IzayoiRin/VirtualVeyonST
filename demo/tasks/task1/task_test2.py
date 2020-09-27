from demo.demo_apps import MoveApps
from demo.tasks.capp import app


@app.task(name="sdc.move21")
def task_1(x):
    return MoveApps(":move", x).foo()


@app.task(name="sdc.move22")
def task_2(x):
    return MoveApps(":move", x + 1).foo()
