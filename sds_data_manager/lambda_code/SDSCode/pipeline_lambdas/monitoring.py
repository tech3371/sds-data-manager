"""Lambda function to send a formatted SNS notification when a Batch job fails."""

import os

import boto3

sns_client = boto3.client("sns")
logs_client = boto3.client("logs")


def lambda_handler(event, context):
    """Lambda handler to send an SNS notification when a Batch job fails.

    Lambda will format the message and retrieve logging from the failed job, before
    sending a message to the notification service (SNS topic defined by the environment
    variable "SNS_ARN").

    Parameters
    ----------
    event : dict
        The JSON formatted document with the data required for the
        lambda function to process. Source event is from AWS Batch.
    context : obj
        The context object for the lambda function
    """
    # Extract relevant details from the event
    detail = event.get("detail", {})

    job_name = detail.get("jobName", "Unknown")
    job_id = detail.get("jobId", "Unknown")
    log_stream_name = (
        detail.get("attempts", [{}])[0].get("container", {}).get("logStreamName", None)
    )

    status_reason = detail.get("statusReason", "No reason provided")

    # Fetch logs if logStreamName is available
    logs = []
    if log_stream_name:
        log_group_name = "/aws/batch/job"
        try:
            response = logs_client.get_log_events(
                logGroupName=log_group_name, logStreamName=log_stream_name, limit=10
            )
            logs = [event["message"] for event in response.get("events", [])]
        except Exception as e:
            logs.append(f"Could not fetch logs: {e!s}")

    # Format email message
    formatted_message = f"""
    Batch Job Failed!

    Job Name: {job_name}
    Job ID: {job_id}
    Status Reason: {status_reason}

    Logs (Last 10 lines):
    {''.join(logs) if logs else 'No logs available'}
    """

    print(f"Formatted Message: {formatted_message}")

    # Send the formatted message to the SNS topic
    sns_client.publish(
        TopicArn=os.environ["SNS_TOPIC_ARN"],
        Subject=f"Batch Job Failure: {job_name}",
        Message=formatted_message,
    )

    return {"statusCode": 200, "body": "Notification sent"}
