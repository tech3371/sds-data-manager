import pytest
from aws_cdk import Stack, aws_lambda, aws_sns
from aws_cdk.assertions import Match, Template

from sds_data_manager.stacks.api_gateway_stack import ApiGateway


@pytest.fixture(scope="module")
def template(app):
    stack = Stack(app, "test-stack")
    test_func = aws_lambda.Function(
        stack,
        "test-function",
        code=aws_lambda.Code.from_inline("def handler(event, context):\n    pass"),
        handler="handler",
        runtime=aws_lambda.Runtime.PYTHON_3_9,
    )
    test_sns_topic = aws_sns.Topic(stack, "test-sns-topic")
    apigw = ApiGateway(
        app,
        construct_id="ApigwTest",
    )
    apigw.deliver_to_sns(sns_topic=test_sns_topic)
    apigw.add_route("test-route", "GET", test_func)
    template = Template.from_stack(apigw)
    return template


def test_apigw_routes(template):
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    # One path resource
    template.resource_count_is("AWS::ApiGateway::Resource", 1)
    template.has_resource_properties(
        "AWS::ApiGateway::Resource",
        props={"PathPart": "test-route"},
    )

    # One GET method on that resource
    template.resource_count_is("AWS::ApiGateway::Method", 1)
    template.has_resource_properties(
        "AWS::ApiGateway::Method",
        props={"HttpMethod": "GET"},
    )


def test_cloudwatch_alarm(template):
    template.resource_count_is("AWS::CloudWatch::Alarm", 1)
    template.has_resource_properties(
        "AWS::CloudWatch::Alarm",
        props={
            "ComparisonOperator": "GreaterThanThreshold",
            "EvaluationPeriods": 60,
            "ActionsEnabled": True,
            "AlarmActions": [{"Fn::ImportValue": Match.string_like_regexp("sns")}],
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
