from pydantic import BaseModel, Field
from typing import Dict, Any, List
from enum import Enum


# Node type schema
class NodeType(str, Enum):
    start = "start"
    message = "message"
    condition = "condition"
    end = "end"

# Message status schema
class MessageStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    opened = "opened"

# Create Node schema
class CreateNodeSchema(BaseModel):
    data: Dict[str, Any] = Field(default={})

# Basic Node schema
class NodeBaseSchema(BaseModel):
    workflow_id: int

    class ConfigDict:
        from_attributes = True

""" Specific nodes classes schemas """

class StartNodeSchema(NodeBaseSchema):
    next_node_id: int

class MessageNodeSchema(NodeBaseSchema):
    message_text: str
    status: MessageStatus
    next_node_id: int

class ConditionNodeSchema(NodeBaseSchema):
    condition: str
    yes_node_id: int
    no_node_id: int

class EndNodeSchema(NodeBaseSchema):
    pass

""" Workflow schemas """
# nodes list for workflow class 
class WorkflowNodeDetailSchema(BaseModel):
    id: int
    node_type: NodeType
    workflow_id: int

    class ConfigDict:
        from_attributes = True

# create workflow object schema
class WorkflowCreateSchema(BaseModel):
    name: str

# detalied workflow schema
class WorkflowSchema(BaseModel):
    id: int
    name: str
    nodes: List[WorkflowNodeDetailSchema]

    class ConfigDict:
        from_attributes = True

