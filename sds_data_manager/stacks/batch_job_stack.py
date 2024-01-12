"""Processing Stack
This is the module containing the general stack to be built for
computation of different algorithms
"""

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_s3 as s3
from constructs import Construct

from sds_data_manager.constructs.batch_compute_resources import FargateBatchResources
from sds_data_manager.stacks.efs_stack import EFSStack


class BatchJobStack(Stack):
    """Batch job stack."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        batch_job_name: str,
        data_bucket: s3.Bucket,
        repo: ecr.Repository,
        db_secret_name: str,
        efs_instance: EFSStack,
        account_name: str,
        **kwargs,
    ) -> None:
        """Constructor

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        vpc : ec2.Vpc
            VPC into which to put the resources that require networking
        batch_job_name : str
            Name of the data product to be processed by this system
        repo : ecr.Repository
            Container repo
        db_secret_name : str
            RDS secrets name
        efs_instance: efs.FileSystem
            EFS stack object
        account_name: str
            account name such as 'dev' or 'prod'
        """
        super().__init__(scope, construct_id, **kwargs)

        self.batch_resources = FargateBatchResources(
            self,
            "FargateBatchEnvironment",
            vpc=vpc,
            processing_step_name=batch_job_name,
            data_bucket=data_bucket,
            repo=repo,
            db_secret_name=db_secret_name,
            efs_instance=efs_instance,
            account_name=account_name,
        )
