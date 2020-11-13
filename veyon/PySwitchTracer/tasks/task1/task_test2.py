from tasks.capp import app
from others.affine_applications import MoveApps


@app.task(name="sdc.move21")
def task_1(x):
    return MoveApps(":move", x).foo()


@app.task(name="sdc.move22")
def task_2(x):
    return MoveApps(":move", x + 1).foo()
