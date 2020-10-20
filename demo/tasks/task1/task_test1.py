from demo.demo_apps import MoveApps
from demo.tasks.capp import app
import time


@app.task(name="sdc.move11", bind=True)
def task_1(self, x):
    time.sleep(1)
    return MoveApps(":move", x).foo()


@app.task(name="sdc.move12", bind=True)
def task_2(self, x):
    return MoveApps(":move", x + 1).foo()
