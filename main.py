import uvicorn
from fastapi import FastAPI
from database import SessionLocal, engine, Base
from routers import workflow as WorkflowRouters, node as NodeRouters

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(WorkflowRouters.router, prefix="")
app.include_router(NodeRouters.router, prefix="/node")

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, workers=3)