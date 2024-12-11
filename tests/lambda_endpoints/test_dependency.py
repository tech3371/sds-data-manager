"""Test data dependency functions."""

import json

from sds_data_manager.lambda_code.SDSCode.pipeline_lambdas import dependency


def test_get_downstream_dependencies():
    "Tests get_downstream_dependencies function."
    event = {
        "dependency_type": "DOWNSTREAM",
        "relationship": "HARD",
        "data_source": "hit",
        "data_type": "l1a",
        "descriptor": "count-rates",
    }

    dependency_response = dependency.lambda_handler(event, None)
    dependents = json.loads(dependency_response["body"])

    expected_complete_dependent = [
        {
            "data_source": "hit",
            "data_type": "l1b",
            "descriptor": "all",
        }
    ]
    assert len(dependents) == 1

    assert dependents == expected_complete_dependent


def test_lambda_handler_no_dependencies():
    """Test lambda_handler when no dependencies are found."""
    event = {
        "data_source": "nonexistent",
        "data_type": "l0",
        "descriptor": "raw",
        "dependency_type": "UPSTREAM",
        "relationship": "HARD",
    }

    response = dependency.lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert response["body"] == "[]"
