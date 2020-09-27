class OPC(object):
    """recieve from app and return plus 1 msg"""
    msg = "recieve: %d"
    mapping = {
        "+": lambda x: x + 1,
        "-": lambda x: x - 1,
        "%": lambda x: x / 2
    }

    def __init__(self, op):
        self.op = op

    def foo(self, x):
        return self.mapping[self.op](x)

    def __call__(self, x):
        return self.msg % self.foo(x)


class Apps(object):

    msg = "send to %s"
    ops = None

    def __init__(self, to: str, x: int):
        self.msg = self.msg % to
        self.x = x

    def foo(self):
        return "{}: {}, {}"\
            .format(self.__class__.__name__, self.msg, self.ops(self.x))


class MoveApps(Apps):
    ops = OPC("+")


class ClickApps(Apps):
    ops = OPC("%")
