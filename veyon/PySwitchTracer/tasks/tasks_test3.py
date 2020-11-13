from tasks.capp import app
from others.affine_applications import ClickApps


@app.task(name="sdc.click3")
def task_1(x):
    return ClickApps(":click", x).foo()
