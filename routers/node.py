from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from database import get_db
from models.workflow import *
from services.node import NodeService
from schemas.workflow import *
router = APIRouter()


@router.post("/create-start-node/", tags=['nodes'])
async def create_start_node(node_data: StartNodeSchema, db: Session = Depends(get_db)):
    created_node = NodeService.create_node(node_type='start', db=db, data=node_data)
    if created_node:
        return created_node
    else:
        return Response(content="Start node for this workflow is already exists.", status_code=200)

@router.post("/create-message-node/", tags=['nodes'])
async def create_message_node(node_data: MessageNodeSchema, db: Session = Depends(get_db)):
    return NodeService.create_node(node_type='message', db=db, data=node_data)

@router.post("/create-condition-node/", tags=['nodes'])
async def create_condition_node(node_data: ConditionNodeSchema, db: Session = Depends(get_db)):
    return NodeService.create_node(node_type='condition', db=db, data=node_data)

@router.post("/create-end-node/", tags=['nodes'])
async def create_end_node(node_data: EndNodeSchema, db: Session = Depends(get_db)):
    created_node = NodeService.create_node(node_type='end', db=db, data=node_data)
    if created_node:
        return created_node
    else:
        return Response(content="End node for this workflow is already exists.", status_code=200)

@router.put('/update-start-node/{node_id}', tags=['nodes'])
async def update_start_node(node_data: StartNodeSchema, node_id: int, db: Session = Depends(get_db)):
    return NodeService.update_node(node_id=node_id, db=db, data=node_data)

@router.put('/update-message-node/{node_id}', tags=['nodes'])
async def update_message_node(node_data: MessageNodeSchema, node_id: int, db: Session = Depends(get_db)):
    return NodeService.update_node(node_id=node_id, db=db, data=node_data)

@router.put('/update-condition-node/{node_id}', tags=['nodes'])
async def update_condition_node(node_data: ConditionNodeSchema, node_id: int, db: Session = Depends(get_db)):
    return NodeService.update_node(node_id=node_id, db=db, data=node_data)

@router.put('/update-end-node/{node_id}', tags=['nodes'])
async def update_end_node(node_data: EndNodeSchema, node_id: int, db: Session = Depends(get_db)):
    return NodeService.update_node(node_id=node_id, db=db, data=node_data)

@router.get("/{node_id}", tags=['nodes'])
async def read_node(node_id: int, db: Session = Depends(get_db)):
    db_node = NodeService.get_node(db=db, node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found.")
    return db_node

@router.delete("/delete/{node_id}", tags=['nodes'])
async def delete_node(node_id: int, db: Session = Depends(get_db)):
    return NodeService.delete_node(db=db, node_id=node_id)

# @router.get('/test')
# async def test(db: Session = Depends(get_db)):
#     return Services.NodeService.test_models(workflow_id=1, db=db)

# @router.post('/create-workflow', tags=['workflows'])
# async def create_workflow(data: WorkflowDTO.WorkflowCreate = None, db: Session = Depends(get_db)):
#     return Services.WorkflowService.create(data.name, db)