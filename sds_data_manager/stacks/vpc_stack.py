from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class VPCStack(Stack):
    """
    Set up Virtual Private Cloud and networking for the app.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with a NAT Gateway

        self.vpc = ec2.Vpc(self, f"VPC-{sds_id}",
                           nat_gateways=1,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name=f"Public-{sds_id}",
                                   subnet_type=ec2.SubnetType.PUBLIC
                               ),
                               ec2.SubnetConfiguration(
                                   subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                   name=f"Private-{sds_id}",
                                   cidr_mask=24
                               ),
                               ec2.SubnetConfiguration(
                                   subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                   name=f"Isolated-{sds_id}",
                                   cidr_mask=24)
                           ])
        
