from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from services.workflow import WorkflowServices
from services.node import NodeService
from schemas.workflow import *

router = APIRouter()

@router.post('/create-workflow', tags=['workflows'])
async def create_workflow(data: WorkflowCreateSchema = None, db: Session = Depends(get_db)):
    return WorkflowServices.create_workflow(data, db)

@router.get('/get/{id}', tags=['workflows'])
async def get_workflow(id: int = None, db: Session = Depends(get_db)):
    workflow = WorkflowServices.get_workflow(db=db, workflow_id=id)
    if workflow:
        return workflow
    else:
        raise HTTPException(status_code=404, detail="Workflow not found.")

@router.put('/update/{id}', tags=['workflows'])
async def update_workflow(workflow_id: int, data: WorkflowSchema, db: Session = Depends(get_db)):
    return WorkflowServices.update_workflow(data=data, db=db, workflow_id=workflow_id)

@router.delete('/delete/{id}', tags=['workflows'])
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    return WorkflowServices.delete_workflow(db=db, workflow_id=workflow_id)

@router.post('/run-sequence/{workflow_id}', tags=['workflows'])
async def run_sequence(workflow_id: int, db: Session = Depends(get_db)):
    return WorkflowServices.create_and_run_graph(db=db, workflow_id=workflow_id)
