import pytest
from schemas.workflow import WorkflowCreateSchema, StartNodeSchema, ConditionNodeSchema, MessageNodeSchema, EndNodeSchema
from routers import workflow as WorkflowRoutes, node as NodeRoutes
from sqlalchemy.orm import sessionmaker
from database import engine


@pytest.fixture(scope="session")
def db():
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

def test_create_start_node(db):
    workflow_data = WorkflowCreateSchema(name="Test")
    workflow = WorkflowRoutes.create_workflow(data=workflow_data, db=db)
    node_data = StartNodeSchema(workflow_id=workflow.id, next_node_id=2)
    node = NodeRoutes.create_start_node(node_data=node_data, db=db)

    assert node.workflow_id == workflow.id
    assert node.next_node_id == 2
    assert node.id in [node.id for node in workflow.nodes]
    db.delete(workflow)
    db.delete(node)
    db.commit()
    
def test_create_message_node(db):
    workflow_data = WorkflowCreateSchema(name="Test")
    workflow = WorkflowRoutes.create_workflow(data=workflow_data, db=db)
    node_data = MessageNodeSchema(workflow_id=workflow.id, next_node_id=2, message_text='test', status='sent')
    node = NodeRoutes.create_message_node(node_data=node_data, db=db)

    assert node.workflow_id == workflow.id
    assert node.message_text == 'test'
    assert node.status == 'sent'
    assert node.id in [node.id for node in workflow.nodes]
    db.delete(workflow)
    db.delete(node)
    db.commit()
    
def test_create_condition_node(db):
    workflow_data = WorkflowCreateSchema(name="Test")
    workflow = WorkflowRoutes.create_workflow(data=workflow_data, db=db)
    node_data = ConditionNodeSchema(workflow_id=workflow.id, condition='status == "sent"', yes_node_id=0, no_node_id=0)
    condition_node = NodeRoutes.create_condition_node(node_data=node_data, db=db)
    message_node_data = MessageNodeSchema(workflow_id=workflow.id, message_text='test', status="sent", next_node_id=condition_node.id)
    message_node = NodeRoutes.create_message_node(node_data=message_node_data, db=db)

    assert condition_node.workflow_id == workflow.id
    assert condition_node.evaluate_condition(db) == True
    assert condition_node.id in [node.id for node in workflow.nodes]
    db.delete(workflow)
    db.delete(condition_node)
    db.delete(message_node)
    db.commit()

def test_create_end_node(db):
    workflow_data = WorkflowCreateSchema(name="Test")
    workflow = WorkflowRoutes.create_workflow(data=workflow_data, db=db)
    node_data = EndNodeSchema(workflow_id=workflow.id)
    node = NodeRoutes.create_end_node(node_data=node_data, db=db)

    assert node.workflow_id == workflow.id
    assert node.id in [node.id for node in workflow.nodes]

    db.delete(workflow)
    db.delete(node)
    db.commit()