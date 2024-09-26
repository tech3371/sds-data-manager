"""Creates RDS PostgreSQL database schema.

Called by a custom resource in the CDK code once the RDS is created/updated.
https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.custom_resources/README.html
"""

import logging

from SDSCode.database import database as db
from SDSCode.database import models
from SDSCode.database.models import Base
from SDSCode.dependency_config import all_dependents

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Entry point to the create schema lambda."""
    logger.info(f"Event: {event}")

    if event.get("RequestType") == "Delete":
        logger.info(
            "Skipping schema modification, only handling Create or Update requests"
        )
        return

    with db.Session() as session:
        if event.get("RequestType") == "Create":
            logger.info("Creating RDS tables")
            # Create tables
            Base.metadata.create_all(db.get_engine())
            session.add_all(all_dependents)

        elif event.get("RequestType") == "Update":
            for dependent in all_dependents:
                existing_record = (
                    session.query(models.PreProcessingDependency)
                    .filter(
                        models.PreProcessingDependency.primary_instrument
                        == dependent.primary_instrument,
                        models.PreProcessingDependency.primary_data_level
                        == dependent.primary_data_level,
                        models.PreProcessingDependency.primary_descriptor
                        == dependent.primary_descriptor,
                        models.PreProcessingDependency.dependent_instrument
                        == dependent.dependent_instrument,
                        models.PreProcessingDependency.dependent_data_level
                        == dependent.dependent_data_level,
                        models.PreProcessingDependency.dependent_descriptor
                        == dependent.dependent_descriptor,
                        models.PreProcessingDependency.relationship
                        == dependent.relationship,
                        models.PreProcessingDependency.direction == dependent.direction,
                    )
                    .first()
                )
                if existing_record is None:
                    session.add(dependent)
                    logger.info(
                        f"Adding new record with {dependent} to the Dependency table."
                    )

    session.commit()
