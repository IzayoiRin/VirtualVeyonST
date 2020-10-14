from demo.demo_apps import ClickApps
from demo.tasks.capp import app


@app.task(name="sdc.click21")
def task_1(x):
    return ClickApps(":click", x).foo()


@app.task(name="sdc.click22")
def tk_2(x):
    return ClickApps(":click", x + 1).foo()
