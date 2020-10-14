import time


class Recorder(object):
    records = None
    blocked = True

    def __init__(self, overflow: int, underflow: int, timeout: float):
        """
        Context Manager for global records list
        :param global records list
        :param overflow: max length of storage(counts)
        :param timeout: blocking releasing time(s), 0 means no releasing during blocking
        """
        self._max = overflow
        self._min = underflow
        self._timeout = float(timeout)

    def link_with_records(self, records):
        self.records = records
        return self

    def blocking_off(self):
        self.blocked = False

    def params(self):
        return {
            "min": self._min, "max": self._max,
            "timeout": self._timeout, "blocked": self.blocked
        }

    def volume_info(self):
        return "@%s<%s>" % (self.records.info(), self.records.id())

    def push(self, rec, blocked=True):
        current = time.time()
        # blocking
        while blocked and (len(self) > self._max):
            time.sleep(0.001)
            spend = round((time.time() - current), 6)
            if self._timeout and (spend >= self._timeout):
                break
        # released
        self.records.append(rec)

    def pop(self, idx=-1, blocked=True):
        current = time.time()
        while blocked and (len(self) <= self._max):
            time.sleep(0.001)
            spend = round((time.time() - current), 6)
            if self._timeout and (spend >= self._timeout):
                break
        try:
            return self.records.pop(idx)
        except IndexError:
            return

    def __len__(self):
        return len(self.records)

    def __str__(self):
        return self.records.__str__()

    def __repr__(self):
        return "<@Recorder:{}>".format(self.records.id())
