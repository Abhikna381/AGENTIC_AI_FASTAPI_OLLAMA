from dotenv import load_dotenv

from fapi import FastAPI,Query
from rq.job import Job
from .client.rq_client import queue, redis_conn
from .queues.worker import process_query
from fastapi.middleware.cors import CORSMiddleware




load_dotenv()

app = FastAPI()



@app.get('/')
def root():
    return {"status": 'Server is up and running'}

@app.post('/chat')
def chat(
        query: str = Query(..., description= "The chat query of user")
):
    
    job = queue.enqueue(process_query, query,job_timeout = -1)

    return {"status": "queued", "job_id": job.id}

@app.get('/job-status')
def get_result(
        job_id: str = Query(..., description="JOB ID")
):
    job = Job.fetch(job_id, connection=redis_conn)

    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result   # ✅ correct way
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)