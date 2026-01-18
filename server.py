# server.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from queue_worker import start_worker, submit_job, get_job

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

    @app.post("/submit")
    def submit(req: JobRequest, ok: bool = Depends(verify_credentials)):
        op = req.op.upper().strip()

        job_key = f"{op}:{req.a}:{req.b}"
        print("Submit job: ", job_key)

        if op == "ADD":
            job_id = submit_job(job_key, add, a=req.a, b=req.b)
        elif op == "MULTIPLY":
            job_id = submit_job(job_key, multiply, a=req.a, b=req.b)
        else:
            raise HTTPException(status_code=400, detail="Unsupported op (use ADD or MULTIPLY)")

        return {"status": "pending", "job_id": job_id}

    @app.get("/result/{job_id}")
    def result(job_id: str, ok: bool = Depends(verify_credentials)):
        print("Get job: ", job_id)
        job = get_job(job_id)

        if job is None:
            raise HTTPException(status_code=404, detail="Unknown job_id")

        # return "processing" until done
        if job["status"] in ["pending", "processing"]:
            return {"status": "processing", "result": None}

        return job  # {"status": "done"/"error", "result": ...}

    return app
