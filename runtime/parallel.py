"""Parallel + distributed runtime — thread/process locally, Ray on Oracle Cloud."""
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from engine.config import USE_RAY, MAX_WORKERS


class ParallelExecutor:
    def __init__(self, kernel, max_workers=MAX_WORKERS, mode="thread"):
        self.kernel = kernel
        self.max_workers = max_workers
        self.mode = mode

    def run(self, tasks):
        if USE_RAY:
            return self._run_ray(tasks)
        if self.mode == "thread":
            return self._run_threads(tasks)
        return self._run_processes(tasks)

    # ── Ray distributed (Oracle Cloud) ────────────────────────────────────────
    def _run_ray(self, tasks):
        try:
            import ray
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True)

            @ray.remote
            def _ray_task(task_ctx, steps):
                from engine.state import State
                from engine.kernel import Kernel
                state = State()
                result = Kernel().run(state, steps=steps)
                return {"task_id": task_ctx["task_id"], "result": result}

            futures = [
                _ray_task.remote(
                    {"task_id": t.task_id},
                    t.context.get("steps", 10)
                )
                for t in tasks
            ]
            raw = ray.get(futures)
            for t, r in zip(tasks, raw):
                t.mark_done(r.get("result"))
            return raw
        except Exception as e:
            # Ray unavailable — fall back to threads
            return self._run_threads(tasks)

    # ── Thread pool (local) ───────────────────────────────────────────────────
    def _run_threads(self, tasks):
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(self._exec_task, t) for t in tasks]
            for f in futures:
                try:
                    results.append(f.result())
                except Exception as e:
                    results.append({"error": str(e)})
        return results

    # ── Process pool (local) ──────────────────────────────────────────────────
    def _run_processes(self, tasks):
        results = []
        with ProcessPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(_process_task, t) for t in tasks]
            for f in futures:
                try:
                    results.append(f.result())
                except Exception as e:
                    results.append({"error": str(e)})
        return results

    def _exec_task(self, task):
        task.mark_running()
        try:
            from engine.state import State
            state = State()
            result = self.kernel.run(state, steps=task.context.get("steps", 10))
            task.mark_done(result)
            return {"task_id": task.task_id, "result": result}
        except Exception as e:
            task.mark_failed(str(e))
            return {"task_id": task.task_id, "error": str(e)}


def _process_task(task):
    from engine.state import State
    from engine.kernel import Kernel
    state = State()
    result = Kernel().run(state, steps=task.context.get("steps", 10))
    return {"task_id": task.task_id, "result": result}
