import queue
import threading
from typing import Any, Dict

tasks = queue.Queue()
results: Dict[str, Dict[str, Any]] = {}
results_lock = threading.Lock()

stop_event = threading.Event()
worker_thread = None


def background_worker():
    while not stop_event.is_set():
        try:
            job_id, func, kwargs = tasks.get(timeout=0.1)
        except queue.Empty:
            continue

        with results_lock:
            results[job_id]["status"] = "processing"

        try:
            out = func(**kwargs)
            with results_lock:
                results[job_id]["status"] = "done"
                results[job_id]["result"] = out
        except Exception as e:
            with results_lock:
                results[job_id]["status"] = "error"
                results[job_id]["result"] = str(e)
        finally:
            tasks.task_done()


def start_worker():
    global worker_thread
    stop_event.clear()
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()


def submit_job(job_id: str, func, **kwargs) -> bool:
    with results_lock:
        if job_id in results:
            return False
        results[job_id] = {"status": "pending", "result": None, "job_id": job_id}

    tasks.put((job_id, func, kwargs))
    return True


def get_job(job_id: str):
    with results_lock:
        return results.get(job_id)
