import time


class Recorder(object):

    def __init__(self, records: list, overflow: int, timeout: float):
        """
        Context Manager for global records list
        :param records: global records list
        :param overflow: max length of storage(counts)
        :param timeout: blocking releasing time(s), 0 means no releasing during blocking
        """
        self.records = records
        self._max = overflow
        self._timeout = float(timeout)
        self._block = True

    def blocking_off(self):
        self._block = False

    def push(self, rec):
        current = time.time()
        # blocking
        while self._block and (len(self.records) > self._max):
            time.sleep(0.001)
            spend = round((time.time() - current), 6)
            if self._timeout and (spend >= self._timeout):
                break
        # released
        self.records.append(rec)

    def __enter__(self):
        print("Current Records: %d" % len(self.records))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: exception handler for Recorder
        print("RECORDS Exit: %d" % len(self.records))
