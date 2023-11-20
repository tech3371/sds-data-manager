from aws_cdk import Stack, aws_sns
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
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.sns_topic_notifications = aws_sns.Topic(
            self, "sns-notifications", display_name="sns-notifications"
        )
