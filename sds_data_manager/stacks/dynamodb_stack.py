# Create stack for dynamoDb
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class DynamoDB(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        table_name: str,
        partition_key: str,
        sort_key: str,
        env,
        on_demand=True,
        read_capacity=1,
        write_capacity=1,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        """
        Parameters
        ----------
        scope : Construct
        construct_id : str
        sds_id : str
            Name suffix for stack
        table_name : str
            Database table name
        partition_key : str
            Partition key for DynamoDB table. The partition key must be unique within a table.
            Every item in a DynamoDB table is uniquely identified by its partition key value.
            DynamoDB uses the partition key to distribute the data across multiple partitions
            for scalability and performance.

            When performing operations such as PutItem, GetItem, or Query in DynamoDB, you need
            to provide a unique value for the partition key to uniquely identify the item. If
            you attempt to insert an item with a partition key value that already exists in the
            table, it will overwrite the existing item with the new data.

            If we want partition key to be not unique, then we need to make sure combination of
            partition key and sort key is unique.

        sort_key : str
            the sort key (also known as the range key) does not have to be unique within a partition.
            Unlike the partition key, the sort key can have duplicate values within a partition.

            The combination of the partition key and sort key together must be unique for each item
            in a DynamoDB table. This means that while multiple items within a partition can have the
            same sort key value, their partition key values must be different.
        env : Environment
            Account and region
        on_demand : bool
            If true, creates on demand DynamoDb table. If false, creates provisioned DynamoDb table.
        read_capacity : int
            Read capacity for provisioned DynamoDb table.
            Default value is 1.
        write_capacity : int
            Write capacity for provisioned DynamoDb table.
            Default value is 1.
        """
        self.sds_id = sds_id
        self.table_name = table_name
        self.partition_key = partition_key
        self.sort_key = sort_key
        self.on_demand = on_demand
        if self.on_demand:
            self._create_on_demand_dynamodb()
        else:
            self._create_provisioned_dynamodb(read_capacity, write_capacity)

    def _create_on_demand_dynamodb(self):
        """Creates On Demand DynamoDb table. On Demand DynamoDb table is created with PAY_PER_REQUEST billing mode.

        When you turn on point-in-time recovery (PITR), DynamoDB backs up your table data automatically so that you
        can restore to any given second in the preceding 35 days.
        Returns
        -------
        Construct
            DynamoDb table construct
        """
        return dynamodb.Table(
            self,
            f"OnDemandDynamoDb-{self.sds_id}",
            table_name=self.table_name,
            partition_key=dynamodb.Attribute(
                name=self.partition_key, type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name=self.sort_key, type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
        )

    def _create_provisioned_dynamodb(self, read_capacity: int, write_capacity: int):
        """Creates Provisioned DynamoDb table. Provisioned DynamoDb table is created with PROVISIONED billing mode.

        When you turn on point-in-time recovery (PITR), DynamoDB backs up your table data automatically so that you
        can restore to any given second in the preceding 35 days.

        Parameters
        ----------
        read_capacity : int
            Read capacity for provisioned DynamoDb table.
        write_capacity : int
            Write capacity for provisioned DynamoDb table.

        Returns
        -------
        Construct
            DynamoDb table construct
        """
        if read_capacity == 1 and write_capacity == 1:
            raise Warning(
                "Read capacity and write capacity are using default values. Please use a different value"
            )
        return dynamodb.Table(
            self,
            f"ProvisionedDynamoDb-{self.sds_id}",
            table_name=self.table_name,
            partition_key=dynamodb.Attribute(
                name=self.partition_key, type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name=self.sort_key, type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            write_capacity=write_capacity,
            read_capacity=read_capacity,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
        )

    def get_table_arn(self, table_name):
        return dynamodb.Table.from_table_name(self, table_name, table_name)
