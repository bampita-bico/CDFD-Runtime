class Task:
    def __init__(self, node, context=None, task_id=None):
        self.node = node
        self.context = context or {}
        self.task_id = task_id
        self.result = None
        self.error = None
        self.status = "pending"

    def mark_running(self):
        self.status = "running"

    def mark_done(self, result):
        self.result = result
        self.status = "done"

    def mark_failed(self, error):
        self.error = error
        self.status = "failed"

    def __repr__(self):
        return f"Task(id={self.task_id}, status={self.status})"
