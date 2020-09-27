from demo.demo_apps import ClickApps
from demo.tasks.capp import app


@app.task(name="sdc.click3")
def task_1(x):
    return ClickApps(":click", x).foo()
