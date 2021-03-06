from tasks.capp import app
from others.affine_applications import ClickApps


@app.task(name="sdc.click21")
def task_1(x):
    return ClickApps(":click", x).foo()


@app.task(name="sdc.click22")
def tk_2(x):
    return ClickApps(":click", x + 1).foo()
