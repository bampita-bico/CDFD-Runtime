from collections import deque


class JobQueue:
    def __init__(self):
        self._queue = deque()
        self._priority_queue = []

    def submit(self, task, priority=0):
        if priority > 0:
            self._priority_queue.append((priority, task))
            self._priority_queue.sort(key=lambda x: -x[0])
        else:
            self._queue.append(task)

    def pop(self):
        if self._priority_queue:
            _, task = self._priority_queue.pop(0)
            return task
        if self._queue:
            return self._queue.popleft()
        return None

    def empty(self):
        return len(self._queue) == 0 and len(self._priority_queue) == 0

    def size(self):
        return len(self._queue) + len(self._priority_queue)

    def drain(self, executor):
        results = []
        while not self.empty():
            task = self.pop()
            if task is not None:
                try:
                    result = executor(task)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        return results


class RayQueue:
    """Stub — replace body with ray.remote calls when Ray is available."""

    def submit_remote(self, fn, *args):
        raise NotImplementedError("Install Ray and replace with ray.remote decorator")
