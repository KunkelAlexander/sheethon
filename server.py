# server.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from queue_worker import start_worker, submit_job, get_job
from disk_cache import DiskCache

# persistent cache file
cache = DiskCache("cache.jsonl")

# Minimum example function - change these to add your own code
def add(a: float, b: float) -> float:
    time_to_compute = 100.0  # simulate long processing
    import time
    time.sleep(time_to_compute)
    return a + b


def multiply(a: float, b: float) -> float:
    time_to_compute = 1.0  # simulate long processing
    import time
    time.sleep(time_to_compute)
    return a * b


# API - this needs to be adapted depending on the function you implement
class JobRequest(BaseModel):
    op: str  # "ADD" or "MULTIPLY"
    a: float
    b: float


def create_app(
    valid_username: str = "user",
    valid_password: str = "pass",
) -> FastAPI:
    app = FastAPI()
    security = HTTPBasic()

    def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
        if credentials.username != valid_username or credentials.password != valid_password:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return True

    # Start worker on startup
    @app.on_event("startup")
    def _startup():
        start_worker()

    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    @app.post("/compute")
    def compute(req: JobRequest, ok: bool = Depends(verify_credentials)):
        op = req.op.upper().strip()
        job_id = f"{op}:{req.a}:{req.b}"

        # 1) Cache hit → done immediately
        cached_value = cache.get(job_id)
        if cached_value is not None:
            print("Use cache")
            return {"status": "done", "job_id": job_id, "cached": True, "result": cached_value}

        # 2) If job doesn't exist yet, create it
        job = get_job(job_id)
        if job is None:
            if op == "ADD":
                submit_job(job_id, add, a=req.a, b=req.b)
            elif op == "MULTIPLY":
                submit_job(job_id, multiply, a=req.a, b=req.b)
            else:
                raise HTTPException(status_code=400, detail="Unsupported op (use ADD or MULTIPLY)")

        # 3) Check current job status (same logic as /result)
        job = get_job(job_id)
        if job is None:
            # should not happen, but safe
            raise HTTPException(status_code=500, detail="Job was not created properly")

        if job["status"] in ["pending", "processing"]:
            return {"status": "processing", "job_id": job_id, "result": None}

        if job["status"] == "done":
            # persist to cache if not already cached
            if cache.get(job_id) is None:
                cache.set(job_id, job["result"])
            return {"status": "done", "job_id": job_id, "cached": False, "result": job["result"]}

        # error case
        return job  # e.g. {"status":"error","result":"..."}
    return app