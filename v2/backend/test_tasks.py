from tasks import execute_workflow_task


def test_dag():
    workflow_data = {
        "id": "wf_1",
        "name": "Test Workflow",
        "nodes": [
            {"id": "node_1", "type": "trigger_manual", "name": "Start", "data": {}},
            {"id": "node_2", "type": "action_gmail", "name": "Send Email", "data": {"to": "test@example.com"}},
            {"id": "node_3", "type": "action_slack", "name": "Notify Team", "data": {}}
        ],
        "edges": [
            {"id": "e1", "source": "node_1", "target": "node_2"},
            {"id": "e2", "source": "node_1", "target": "node_3"}
        ]
    }

    result = execute_workflow_task.run(workflow_data)
    assert result["status"] == "completed"
    assert "node_1" in result["results"]
    assert "node_2" in result["results"]
    assert "node_3" in result["results"]

    print("Execution Result:", result)


if __name__ == "__main__":
    test_dag()
