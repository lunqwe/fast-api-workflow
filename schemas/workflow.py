from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class NodeType(str, Enum):
    start = "start"
    message = "message"
    condition = "condition"
    end = "end"

class MessageStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    opened = "opened"

class CreateNodeSchema(BaseModel):
    data: Dict[str, Any] = Field(default={})

class NodeBaseSchema(BaseModel):
    workflow_id: int

    class ConfigDict:
        from_attributes = True

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

class WorkflowNodeDetailSchema(BaseModel):
    id: int
    node_type: NodeType
    workflow_id: int

    class ConfigDict:
        from_attributes = True

class WorkflowCreateSchema(BaseModel):
    name: str

class WorkflowSchema(BaseModel):
    id: int
    name: str
    nodes: List[WorkflowNodeDetailSchema]

    class ConfigDict:
        from_attributes = True

