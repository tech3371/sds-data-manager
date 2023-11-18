import pytest
from aws_cdk import Stack, aws_apigateway
from aws_cdk.assertions import Match, Template

from sds_data_manager.stacks.monitoring_stack import MonitoringStack


@pytest.fixture(scope="module")
def template(app):
    # Set up inputs to the monitoring stack
    stack = Stack(app, "TestStack")
    api = aws_apigateway.RestApi(stack, "TestApi")
    # Need to add a method to the API
    api.root.add_method("GET")

    monitor = MonitoringStack(
        app,
        construct_id="MonitorTest",
        api=api,
    )

    template = Template.from_stack(monitor)

    return template


def test_monitoring(template):
    template.resource_count_is("AWS::CloudWatch::Alarm", 1)
    template.has_resource_properties(
        "AWS::CloudWatch::Alarm",
        props={
            "ComparisonOperator": "GreaterThanThreshold",
            "EvaluationPeriods": 60,
            "ActionsEnabled": True,
            "AlarmActions": [{"Ref": Match.string_like_regexp("sns")}],
            "DatapointsToAlarm": 1,
            "Dimensions": [{"Name": "ApiName", "Value": Match.any_value()}],
            "MetricName": "Latency",
            "Namespace": "AWS/ApiGateway",
            "Period": 60,
            "Statistic": "Maximum",
            "Threshold": 10000,
            "TreatMissingData": "notBreaching",
        },
    )
