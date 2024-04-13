from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Session
from database import Base 
import rule_engine

# Workflow model
class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    nodes = relationship("Node", back_populates="workflow", cascade='all, delete')

# Base node model
class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String)  # Node type (start, message, condition, end)
    workflow_id = Column(Integer, ForeignKey('workflows.id'))
    workflow = relationship("Workflow", back_populates="nodes", cascade='all, delete')

    __mapper_args__ = {
        'polymorphic_on': node_type
    }

    
class StartNode(Node):
    __tablename__ = 'start_nodes'

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True, index=True)
    next_node_id = Column(Integer, ForeignKey('nodes.id'))
    next_node = relationship("Node", foreign_keys=[next_node_id])

    __mapper_args__ = {
        'inherit_condition': id == Node.id,
        'polymorphic_identity': 'start'
    }


class MessageNode(Node):
    __tablename__ = 'message_nodes'

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True, index=True)
    message_text = Column(String)
    status = Column(Enum('pending', 'sent', 'opened'))
    next_node_id = Column(Integer, ForeignKey('nodes.id'))
    next_node = relationship("Node", foreign_keys=[next_node_id])

    __mapper_args__ = {
        'inherit_condition': id == Node.id,
        'polymorphic_identity': 'message'
    }

class ConditionNode(Node):
    __tablename__ = 'condition_nodes'

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True, index=True)
    condition = Column(String)
    yes_node_id = Column(Integer, ForeignKey('nodes.id'))
    no_node_id = Column(Integer, ForeignKey('nodes.id'))
    yes_node = relationship("Node", foreign_keys=[yes_node_id])
    no_node = relationship("Node", foreign_keys=[no_node_id])

    def evaluate_condition(self, db: Session):
        """
        Evaluates the condition for a node of type ConditionNode.

        Args:
            db (Session): The SQLAlchemy database session.

        Returns:
            bool: True if the condition evaluates to True, False otherwise.

        Raises:
            ValueError: If an unexpected error occurs.
        """
        rule = rule_engine.Rule(self.condition)

        connected_message_node = db.query(MessageNode).filter(MessageNode.next_node_id == self.id).first()

            # Finding connected nodes of type ConditionNode
        connected_condition_node = db.query(ConditionNode).filter(ConditionNode.no_node_id == self.id).first()

        print('cond:', connected_message_node)
        if connected_message_node:
                # If a connected node of type MessageNode is found, check the condition based on it
            rule_dict = {
                'status': str(connected_message_node.status),
            }

            if rule.matches(rule_dict):
                return True
            else:
                return False
        elif connected_condition_node:
                # If a connected node of type ConditionNode is found, get the previous node of type MessageNode
            previous_message_node = db.query(MessageNode).filter(MessageNode.next_node_id == connected_condition_node.id).first()

            if previous_message_node:
                    # If the previous node of type MessageNode is found, check the condition based on it
                try:
                    rule_dict = {
                        'status': str(previous_message_node.status),
                    }
                    if rule.matches(rule_dict):
                        return True
                    else:
                        return False
                except:
                    raise ValueError("Rule error")
            else:
                raise ValueError('Unforeseen error')
        else:
            raise ValueError('Condition Node has no connected message nodes')

    __mapper_args__ = {
        'inherit_condition': id == Node.id,
        'polymorphic_identity': 'condition'
    }

class EndNode(Node):
    __tablename__ = 'end_nodes'

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True, index=True)

    __mapper_args__ = {
        'inherit_condition': id == Node.id,
        'polymorphic_identity': 'end'  # Указываем идентификатор полиморфизма
    }