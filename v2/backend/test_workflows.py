"""
Integration tests for the Ultra-Lightweight Workflow Engine
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from tasks import build_execution_order, execute_workflow_task
from schemas import WorkflowSchema, Node, NodeData, Edge
from db import init_db, get_execution_history
import json

# Create test client
client = TestClient(app)


@pytest.fixture
def setup_db():
    """Initialize database for tests"""
    init_db()
    yield


class TestWorkflowEndpoints:
    """Test workflow API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_node_catalog(self):
        """Test node catalog endpoint"""
        response = client.get("/api/nodes/schema")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert len(data["nodes"]) > 0
        
        # Check that we have expected pieces
        piece_names = [node["name"] for node in data["nodes"]]
        assert "gmail" in piece_names
        assert "slack" in piece_names
        assert "manual" in piece_names
        assert "condition" in piece_names
    
    def test_get_piece_schema(self):
        """Test getting schema for a specific piece"""
        response = client.get("/api/nodes/schema/gmail")
        assert response.status_code == 200
        data = response.json()
        assert data["piece_name"] == "gmail"
        assert "schema" in data
        assert "properties" in data["schema"]
        
        # Check that gmail schema has expected fields
        schema_properties = data["schema"]["properties"]
        assert "email_to" in schema_properties
        assert "subject" in schema_properties
        assert "body" in schema_properties
    
    def test_get_piece_schema_not_found(self):
        """Test getting schema for non-existent piece"""
        response = client.get("/api/nodes/schema/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
    
    def test_execute_workflow_empty(self, setup_db):
        """Test executing an empty workflow"""
        workflow = WorkflowSchema(
            workflow_id="test_empty",
            nodes=[],
            edges=[]
        )
        response = client.post("/api/workflows/execute", json=workflow.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "dispatched"
    
    def test_execute_workflow_with_nodes(self, setup_db):
        """Test executing a workflow with nodes"""
        nodes = [
            Node(
                id="node1",
                data=NodeData(
                    label="Manual Trigger",
                    piece="manual",
                    config={}
                ),
                position={"x": 0, "y": 0}
            ),
            Node(
                id="node2",
                data=NodeData(
                    label="Send Email",
                    piece="gmail",
                    config={
                        "email_to": "test@example.com",
                        "subject": "Test Email",
                        "body": "This is a test"
                    }
                ),
                position={"x": 200, "y": 0}
            )
        ]
        edges = [
            Edge(source="node1", target="node2", id="edge1")
        ]
        
        workflow = WorkflowSchema(
            workflow_id="test_with_nodes",
            nodes=nodes,
            edges=edges
        )
        response = client.post("/api/workflows/execute", json=workflow.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "dispatched"
    
    def test_execution_history(self, setup_db):
        """Test execution history endpoint"""
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestDAGExecutionOrder:
    """Test DAG execution order logic"""
    
    def test_single_node(self):
        """Test execution order with single node"""
        nodes = [{"id": "node1", "data": {"piece": "gmail"}}]
        edges = []
        
        order = build_execution_order(nodes, edges)
        assert order == ["node1"]
    
    def test_linear_workflow(self):
        """Test execution order with linear workflow (A -> B -> C)"""
        nodes = [
            {"id": "node1", "data": {"piece": "manual"}},
            {"id": "node2", "data": {"piece": "gmail"}},
            {"id": "node3", "data": {"piece": "slack"}}
        ]
        edges = [
            {"source": "node1", "target": "node2"},
            {"source": "node2", "target": "node3"}
        ]
        
        order = build_execution_order(nodes, edges)
        assert order == ["node1", "node2", "node3"]
    
    def test_parallel_workflow(self):
        """Test execution order with parallel branches"""
        nodes = [
            {"id": "trigger", "data": {"piece": "manual"}},
            {"id": "gmail", "data": {"piece": "gmail"}},
            {"id": "slack", "data": {"piece": "slack"}},
            {"id": "merge", "data": {"piece": "condition"}}
        ]
        edges = [
            {"source": "trigger", "target": "gmail"},
            {"source": "trigger", "target": "slack"},
            {"source": "gmail", "target": "merge"},
            {"source": "slack", "target": "merge"}
        ]
        
        order = build_execution_order(nodes, edges)
        # Both gmail and slack should come after trigger, and before merge
        assert order[0] == "trigger"
        assert "gmail" in order[1:3]
        assert "slack" in order[1:3]
        assert order[-1] == "merge"
    
    def test_circular_reference_error(self):
        """Test that circular references raise an error"""
        nodes = [
            {"id": "node1", "data": {"piece": "gmail"}},
            {"id": "node2", "data": {"piece": "slack"}}
        ]
        edges = [
            {"source": "node1", "target": "node2"},
            {"source": "node2", "target": "node1"}  # Circular reference
        ]
        
        with pytest.raises(Exception) as exc_info:
            build_execution_order(nodes, edges)
        assert "circular" in str(exc_info.value).lower()
    
    def test_disconnected_nodes(self):
        """Test execution order with disconnected nodes"""
        nodes = [
            {"id": "node1", "data": {"piece": "gmail"}},
            {"id": "node2", "data": {"piece": "slack"}}
        ]
        edges = []  # No connections
        
        order = build_execution_order(nodes, edges)
        assert len(order) == 2
        assert "node1" in order
        assert "node2" in order


class TestNodeSchemas:
    """Test node schema definitions"""
    
    def test_workflow_schema_validation(self):
        """Test workflow schema validation"""
        # Valid workflow
        workflow = WorkflowSchema(
            workflow_id="test",
            nodes=[
                Node(
                    id="node1",
                    data=NodeData(
                        label="Test Node",
                        piece="gmail",
                        config={"email_to": "test@example.com"}
                    ),
                    position={"x": 0, "y": 0}
                )
            ],
            edges=[]
        )
        assert workflow is not None
        assert workflow.workflow_id == "test"
        assert len(workflow.nodes) == 1
    
    def test_node_data_validation(self):
        """Test node data validation"""
        node_data = NodeData(
            label="Test",
            piece="gmail",
            config={"email_to": "test@example.com"}
        )
        assert node_data.label == "Test"
        assert node_data.piece == "gmail"
        assert node_data.config["email_to"] == "test@example.com"
    
    def test_edge_validation(self):
        """Test edge validation"""
        edge = Edge(source="node1", target="node2", id="edge1")
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.id == "edge1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
