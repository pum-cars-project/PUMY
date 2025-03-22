from fastapi import FastAPI
from application.pipeline_service import PipelineService
from application.predictions.model_service import ModelService
from api.jobs import CreateNewJobRequest, CreateNewJobResponse
from infrastructure.database.database_service import DatabaseService

app = FastAPI()
pipeline_service = PipelineService()
model_service = ModelService()
database_service = DatabaseService()


@app.get("/models")
async def get_models():
    return {"message": "Not implemented"}


@app.get("/pipeline/jobs")
async def get_pipeline_jobs():
    return {"message": "Not implemented"}


@app.get("/pipeline/jobs/{job_id}")
async def get_job_status(job_id: str):
    return pipeline_service.get_job_status(job_id)


@app.post("/pipeline/jobs/new", response_model=CreateNewJobResponse)
async def create_new_pipeline_job(request: CreateNewJobRequest):
    new_job_id = pipeline_service.create_new_job(request)
    return CreateNewJobResponse(job_id=new_job_id)


def setup() -> None:
    pass
