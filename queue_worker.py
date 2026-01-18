from collections import deque
import threading
import time
import uuid

tasks_queue = deque()
queue_lock = threading.Lock()

results = {}  # job_id -> {"status": "pending|processing|done|error", "result": any}
results_lock = threading.Lock()

stop_event = threading.Event()
worker_thread = None


def background_worker():
    while not stop_event.is_set():
        item = None

        with queue_lock:
            if tasks_queue:
                item = tasks_queue.popleft()

        if item is None:
            time.sleep(0.1)
            continue

        job_id, func, kwargs = item

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


def start_worker():
    global worker_thread
    stop_event.clear()
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()


def stop_worker():
    global worker_thread
    stop_event.set()
    if worker_thread:
        worker_thread.join()


def submit_job(job_id: str, func, **kwargs) -> str:
    with results_lock:
        if job_id in results:
            # If it already exists, do not enqueue again
            return job_id
        results[job_id] = {"status": "pending", "result": None}

    with queue_lock:
        tasks_queue.append((job_id, func, kwargs))

    return job_id


def get_job(job_id: str):
    with results_lock:
        return results.get(job_id)
