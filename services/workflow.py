from fastapi import HTTPException, Depends
import networkx as nx
from models.workflow import Workflow, StartNode, EndNode, MessageNode, ConditionNode
from schemas.workflow import *
from sqlalchemy.orm import Session
from database import get_db


class WorkflowServices:
    def create_workflow(data: WorkflowCreateSchema, db: Session = Depends(get_db())) -> Workflow:
        workflow = Workflow(name=data.name)

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        print(workflow.id)
        return workflow
    
    def get_workflow(db: Session, workflow_id: int):
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            print(workflow.nodes)
            return workflow
        else:
            return False
    
    def update_workflow(workflow_id: int, data: WorkflowSchema, db: Session = Depends(get_db())):
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        workflow.name = data.name

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        return workflow
        

    def delete_workflow(workflow_id: int, db: Session = Depends(get_db())):
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        print(workflow.id)
        if workflow:
            db.delete(workflow)   
            db.commit()
            return True
        else:
            raise HTTPException(status_code=400, detail=f"Workflow doesn`t exists.")



    def create_and_run_graph(db: Session, workflow_id: int) -> nx.DiGraph:
            """
            Run the workflow represented by models relations

            Args:
                G (nx.DiGraph): The directed graph representing the workflow.
                start_node (int): The ID of the start node.
                last_node (int): The ID of the last node.
                node_types (dict): Determined types of nodes

            Returns:
                dict: A dictionary containing the success path and edges of the workflow.
            """
            workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                raise HTTPException(status_code=400, detail= f"Error. Workflow not found")

            # create empty graph
            G = nx.DiGraph()

            # add nodes to graph
            for node in workflow.nodes:
                G.add_node(node.id)

            # create graph edges
            last_node = 0
            for node in workflow.nodes:
                if isinstance(node, StartNode):
                    if node.next_node.node_type != 'condition':
                        G.add_edge(node.id, node.next_node_id)
                        start_node = node.id
                    else:
                        raise HTTPException(status_code=400, detail="Error. Condition node could be reached through Message or Condition node")

                elif isinstance(node, MessageNode):
                    G.add_edge(node.id, node.next_node_id)

                elif isinstance(node, ConditionNode):
                    condition_value = node.evaluate_condition(db=db)
                    if condition_value:
                        G.add_edge(node.id, node.yes_node_id)
                        G.add_edge(node.id, node.no_node_id, weight=999) 
                    else:
                        G.add_edge(node.id, node.yes_node_id, weight=999)
                        G.add_edge(node.id, node.no_node_id) 

                elif isinstance(node, EndNode):
                    last_node = node.id


            if not last_node:
                raise HTTPException(status_code=400, detail="Error. Sequence has no end node.")
            
            reachable_nodes = nx.bfs_tree(G, source=start_node).nodes()

            if last_node not in reachable_nodes:
                raise HTTPException(status_code=400, detail="Error. End node is unreachable.")
            
            edges = []
            for edge in G.edges:
                edges.append(edge)

            if not edges:
                raise HTTPException(status_code=400, detail="Error. Created graph has no edges.")

            sequence = nx.shortest_path(G, target=last_node)[start_node]

            response_data = {
                'success_path': sequence,
                'edges': edges
            }
            
            return response_data
    

