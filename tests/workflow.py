import pytest
from services.workflow import WorkflowServices
from services.node import NodeService
from schemas.workflow import WorkflowCreateSchema, StartNodeSchema, ConditionNodeSchema, MessageNodeSchema, EndNodeSchema
from routers import workflow as WorkflowRoutes, node as NodeRoutes
from sqlalchemy.orm import sessionmaker
from database import engine
import asyncio


@pytest.fixture(scope="session")
def db():
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_workflow(db):
    workflow_name = "Test Workflow"
    workflow_data = WorkflowCreateSchema(name=workflow_name)
    created_workflow = asyncio.run(WorkflowRoutes.create_workflow(data=workflow_data, db=db))

    assert created_workflow.name == workflow_name

    db.delete(created_workflow)
    db.commit()

def test_update_workflow(db):
    workflow_name = "Test Workflow"
    new_workflow_name = "Updated Workflow"
    workflow_to_update = asyncio.run(WorkflowRoutes.create_workflow(data=WorkflowCreateSchema(name=workflow_name), db=db))

    updated_workflow = asyncio.run(WorkflowRoutes.update_workflow(workflow_id=workflow_to_update.id, data=WorkflowCreateSchema(name=new_workflow_name), db=db))

    assert updated_workflow.id == workflow_to_update.id
    assert updated_workflow.name == new_workflow_name

    db.delete(updated_workflow)
    db.commit()

def test_delete_workflow(db):
    workflow_name = "Test Workflow"
    workflow = asyncio.run(WorkflowRoutes.create_workflow(data=WorkflowCreateSchema(name=workflow_name), db=db))
    deleted_workflow = asyncio.run(WorkflowRoutes.delete_workflow(workflow_id=workflow.id, db=db))

    assert deleted_workflow == 1
    


def test_create_and_run_graph(db): # Valid data 

    workflow_data = WorkflowCreateSchema(name='test')
    workflow = asyncio.run(WorkflowRoutes.create_workflow(data=workflow_data, db=db))
    print('id', workflow.id)

    # Creating nodes with no edges
    start_node_data = StartNodeSchema(workflow_id=workflow.id, next_node_id=0)
    message_node_data = MessageNodeSchema(workflow_id=workflow.id, message_text='test', status='sent', next_node_id=0)
    condition_node_data = ConditionNodeSchema(workflow_id=workflow.id, yes_node_id=0, no_node_id=0, condition="status == 'sent'")
    yes_node_data = MessageNodeSchema(workflow_id=workflow.id, message_text='yes message node', status='sent', next_node_id=0)
    no_node_data = MessageNodeSchema(workflow_id=workflow.id, message_text='no message node', status='sent', next_node_id=0)
    end_node_data = EndNodeSchema(workflow_id=workflow.id)

    start_node = asyncio.run(NodeRoutes.create_start_node(node_data=start_node_data, db=db))
    message_node = asyncio.run(NodeRoutes.create_message_node(node_data=message_node_data, db=db))
    condition_node = asyncio.run(NodeRoutes.create_condition_node(node_data=condition_node_data, db=db))
    no_node = asyncio.run(NodeRoutes.create_message_node(node_data=no_node_data, db=db))
    yes_node = asyncio.run(NodeRoutes.create_message_node(node_data=yes_node_data, db=db))
    end_node = asyncio.run(NodeRoutes.create_end_node(node_data=end_node_data, db=db))

    # updating nodes edges with exist nodes
    start_node_data = StartNodeSchema(workflow_id=workflow.id, next_node_id=message_node.id)
    asyncio.run(NodeRoutes.update_start_node(node_id=start_node.id, node_data=start_node_data, db=db))

    message_node_data = MessageNodeSchema(workflow_id=workflow.id, message_text='test', status='sent', next_node_id=condition_node.id)
    asyncio.run(NodeRoutes.update_message_node(node_data=message_node_data, node_id=message_node.id, db=db))

    condition_node_data = ConditionNodeSchema(workflow_id=workflow.id, yes_node_id=yes_node.id, no_node_id=no_node.id, condition="status == 'sent'")
    asyncio.run(NodeRoutes.update_condition_node(node_data=condition_node_data, node_id=condition_node.id, db=db))

    yes_node_new_data = MessageNodeSchema(workflow_id=workflow.id, message_text='yes message node', status='sent', next_node_id=end_node.id)
    asyncio.run(NodeRoutes.update_message_node(node_data=yes_node_new_data , node_id=yes_node.id, db=db))

    no_node_new_data = MessageNodeSchema(workflow_id=workflow.id, message_text='no message node', status='sent', next_node_id=start_node.id)
    asyncio.run(NodeRoutes.update_message_node(node_data=no_node_new_data , node_id=no_node.id, db=db))

    # Running sequence
    result = asyncio.run(WorkflowRoutes.run_sequence(workflow_id=workflow.id, db=db))

    assert 'success_path' in result
    assert 'edges' in result

    assert result['success_path'] == [start_node.id, message_node.id, condition_node.id, yes_node.id, end_node.id]
    assert (start_node.id, message_node.id) in result['edges']
    assert (message_node.id, condition_node.id) in result['edges']
    assert (condition_node.id, yes_node.id) in result['edges']
    assert (yes_node.id, end_node.id) in result['edges']

    for node in workflow.nodes:
        node.yes_node = None
        node.no_node = None
        node.next_node = None
        node.workflow = None
        NodeService.delete_node(node_id=node.id, db=db)

    WorkflowServices.delete_workflow(workflow_id=workflow.id, db=db)
    db.commit()
