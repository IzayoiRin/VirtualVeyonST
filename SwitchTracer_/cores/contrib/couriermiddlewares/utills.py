import threading

import numpy as np


def _binary_sorted(temp, results: list, ordered_asc: bool, primary=None):
    n = len(results)
    if n == 0:
        results.append(temp)
    low, high = 0, n-1
    while low <= high:
        mid = np.floor((low + high)/2).astype(np.int)
        flag = (primary(results[mid]) > primary(temp)) if callable(primary) \
            else (results[mid] > temp)
        if flag == ordered_asc:
            high = mid - 1
        else:
            low = mid + 1
    results.insert(high + 1, temp)


def binary_sort_copied(array: iter, ordered_asc=True, filter_=None, primary: int = None) -> list:
    """
    Binary insert sorting for 1D or 2D array and return the sorted array copy.
    Best: O(Nlog2(N)) Average: O(N^2) Worst: O(N^2)

    Example:
    np.random.seed(0)
    R = np.random.randint(0, 8, (20, 2))
    sorted_arr = binary_sort_copied(
        R, ordered_asc=False,
        filter_=lambda x: x if x[0] > 3 else None,
        primary=0
    )
    print(np.array(sorted_arr))

    :param array: sorting array.
    :param ordered_asc: sorted order, default ASC.
    :param filter_: filter function, return None repr masked.
    :param primary: the compare primary idm repr compared primary idx of 2D array's element.
    :return: sorted array
    """
    ret = []
    filter_ = filter_ or (lambda x: x)
    primary_ = (lambda x: x[primary]) if isinstance(primary, int) else None
    for temp in array:
        temp = filter_(temp)
        if temp is not None:
            _binary_sorted(temp, ret, ordered_asc, primary_)
    return ret


class BaseMessageQueue(object):

    def __init__(self, mq=None):
        self.mq = mq or list()

    def __len__(self):
        return len(self.mq)

    def queue(self, x):
        self.mq.append(x)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.mq.pop(0)

    def is_empty(self):
        return not bool(len(self.mq))

    def show(self, mod: str, filter_=None):
        show = getattr(self, "%s_show" % mod.lower(), None)
        if show:
            show(filter_)
        raise NotImplementedError


class TempMessageQueue(BaseMessageQueue):

    def queue_show(self, filter_=None):
        print("#" * 10, "MESSAGE QUEUE", "#" * 10)
        count = 0
        while not self.is_empty() and count < len(self):
            x = self.dequeue()
            if filter_ is None or filter_(x):
                print(x)
            self.queue(x)
            count += 1
        print("#" * 35)


class EnhancedTempMassageQueue(BaseMessageQueue):

    def iloc_set(self, idx, value):
        self.mq[idx] = value

    def iloc_show(self, filter_=None):
        print("#" * 10, "MESSAGE QUEUE", "#" * 10)
        for i in self.mq:
            if filter_ is None or filter_(i):
                print(i)
        print("#" * 35)


MESSAGE_QUEUE = EnhancedTempMassageQueue()
TASK_QUEUE = TempMessageQueue()


class AtomicVolume(object):

    def __init__(self, vol,  blocking=True, timeout=-1):
        self.__vol = vol
        self.__vol_default = vol.copy()
        self.mutex = threading.RLock()
        self.blocking = blocking
        self.timeout = timeout

    def reset(self):
        self.__vol = self.__vol_default.copy()

    @property
    def volume(self):
        return self.__vol.copy()

    def write(self, func, args: tuple = (), kwargs: dict = None, callback_=None, protected=True):
        # protected mode: Mutex locked
        if protected:
            self.mutex.acquire(self.blocking, self.timeout)
        # check param<func> whether callable
        if not callable(func):
            raise TypeError("param<func> must be callable!")
        # exec write operation
        try:
            return func(self.__vol, *args, **(kwargs or dict()))
        except Exception as e:
            # catch exception through callback function
            if callable(callback_):
                return callback_(e)
            raise e
        # protected mode: Mutex released
        finally:
            if protected:
                self.mutex.release()


def expr_redis_updates():
    import time
    MAX_EPOCH = int(5 * 1e5)
    blocks, slavers, max_connects = 96, 30, 16
    col0 = np.array([list(range(blocks)) for _ in range(slavers)]).reshape(-1, 1)
    col1 = np.array([np.repeat(i, blocks) for i in range(slavers)]).reshape(-1, 1)
    mat = np.hstack([col0, col1])
    indices = np.arange(mat.shape[0])

    def epoch():
        update_times = 0
        rec_slavers = set()
        while len(rec_slavers) < slavers:
            idx = np.random.choice(indices, max_connects, replace=False)
            for i in mat[idx, 1]:
                rec_slavers.add(i)
            update_times += 1
        return update_times

    ret = 0
    step, low, k, patient = MAX_EPOCH // 50, 0, 1000.0, 4
    T = time.time()
    speed, last = 0, 0
    for e in range(1, MAX_EPOCH + 1):
        ret += epoch()
        cal = np.floor(e * 50 / MAX_EPOCH).astype(np.int)
        if time.time() - T:
            speed = e / (time.time() - T)
            last = (MAX_EPOCH - e) / speed
        if low == 0:
            low = ret / e
        if e % step == 0:
            nk = (ret / e - low) / step
            ddk = (nk - k) / step
            if ddk > 0:
                patient -= 1
            if patient == 0:
                break
            low, k = ret / e, nk
        print("\rEpoch: %s<patient: %d>[%.2f ep0ch/s - %.2f s] %s%s" % (
            e,
            patient,
            speed,
            last,
            "#" * cal,
            "-" * (50 - cal)
        ), end="")
    print()
    print("Experience of update times: %.4f" % (ret / e))
