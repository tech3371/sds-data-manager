"""Stack for creating instrument SQS queues and attaching batch_starter as a target."""

from aws_cdk import Stack, aws_sqs
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from constructs import Construct


class SqsStack(Stack):
    """Stack to create instrument/level SQS queues and attach them to EventBridge."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        instrument_name: str,
        **kwargs,
    ):
        """Create a stack to create a SQS queue and Eventbridge rule for an instrument.

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        instrument_name : str
            The name of the instrument.
        kwargs : dict
            Keyword arguments
        """
        super().__init__(scope, construct_id, **kwargs)

        # Event has filename in it, we need an EventPattern that matches that
        # EventBridge Rule for the SQS queue
        event_from_indexer = events.Rule(
            self,
            f"{instrument_name}FileArrived",
            rule_name=f"{instrument_name}_file_arrived",
            event_pattern=events.EventPattern(
                source=["imap.lambda"],
                detail_type=["Processed File"],
                detail={
                    "object": {
                        "key": [{"exists": True}],
                        "instrument": [instrument_name],
                    },
                },
            ),
        )

        # This is not a FIFO queue because it isn't required. Anything reading
        # from this queue should be resistant to duplicate events or out of order
        # events.
        self.instrument_queue = aws_sqs.Queue(
            self,
            f"{instrument_name}FileArrivalQueue",
            queue_name=f"{instrument_name}_file_arrival_queue",
        )

        # TODO Add target to SQS
        event_from_indexer.add_target(targets.SqsQueue(self.instrument_queue))

        # event_from_indexer_lambda.add_target(
        #     targets.LambdaFunction(self.instrument_lambda)
        # )
