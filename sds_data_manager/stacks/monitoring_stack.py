from aws_cdk import Duration, Stack, aws_apigateway, aws_sns
from aws_cdk import aws_cloudwatch as cw
from aws_cdk import aws_cloudwatch_actions as cw_actions
from constructs import Construct


class MonitoringStack(Stack):
    """Monitoring stack

    Set up an integration with Slack to send notifications to a channel.

    This had to be done manually in the AWS console to authorize the
    AWS account to use the Slack app.
    Just follow the steps here to create a new Slack authorization.
    https://us-east-2.console.aws.amazon.com/chatbot/home
    Choosing the channel and permissions as you go through the steps.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api: aws_apigateway.RestApi,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.sns_topic = aws_sns.Topic(
            self, "slack-sns-notifications", display_name="slack-sns-notifications"
        )

        # Define the metric the alarm is based on
        # List of Metric options for API Gateway:
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html
        metric = cw.Metric(
            namespace="AWS/ApiGateway",
            metric_name="Latency",
            dimensions_map={"ApiName": api.rest_api_name},
            period=Duration.minutes(1),
            statistic="Maximum",
        )

        # Define the alarm
        self.cw_alarm = cw.Alarm(
            self,
            "apigw-cw-alarm",
            alarm_name="apigw-cw-alarm",
            alarm_description="API Gateway latency is high",
            actions_enabled=True,
            metric=metric,
            # Evaluate the metric over the past 60 minutes
            # alarming if any single datapoint is over the threshold
            # This will limit the alarm to once/hour
            evaluation_periods=60,
            datapoints_to_alarm=1,
            # If the maximum latency is greater than 10 seconds, send a notification
            threshold=10 * 1000,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
        )
        # Send notification to Slack
        self.cw_alarm.add_alarm_action(cw_actions.SnsAction(self.sns_topic))
