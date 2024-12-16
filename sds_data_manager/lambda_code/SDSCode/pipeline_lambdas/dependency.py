"""Dependency tracking module."""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import imap_data_access

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class DataSource:
    """Valid data sources for dependency tracking.

    Valid data sources includes valid instruments names
    from imap_data_access and other data sources related to SPICE.
    """

    SC_ATTITUDE: str = "sc_attitude"
    SC_EPHEMERIS: str = "sc_ephemeris"
    PLANET_EPHEMERIS: str = "planet_ephemeris"
    TIME_KERNEL: str = "time_kernel"
    THRUSTER_FIRE_KERNEL: str = "thruster_fire_kernel"
    SC_SPIN: str = "sc_spin"
    SC_REPOINT: str = "sc_repoint"
    SC_POINTING_FRAME: str = "sc_pointing_frame"

    @property
    def valid_source(self) -> list[str]:
        """Add data sources.

        Returns
        -------
        list[str]
            list of valid data sources.
        """
        return [
            self.SC_ATTITUDE,
            self.SC_EPHEMERIS,
            self.PLANET_EPHEMERIS,
            self.TIME_KERNEL,
            self.THRUSTER_FIRE_KERNEL,
            self.SC_SPIN,
            self.SC_REPOINT,
            self.SC_POINTING_FRAME,
            *imap_data_access.VALID_INSTRUMENTS,
        ]


@dataclass
class DataType:
    """Valid data types for dependency tracking.

    Valid data types includes valid data levels from imap_data_access
    and other data types related to SPICE and ancillary data.
    """

    SPICE: str = "spice"
    ANCILLARY: str = "ancillary"

    @property
    def valid_type(self) -> list[str]:
        """Add data types.

        Returns
        -------
        list[str]
            list of valid data types.
        """
        return [
            self.SPICE,
            self.ANCILLARY,
            *imap_data_access.VALID_DATALEVELS,
        ]


@dataclass
class DataDescriptor:
    """Valid data descriptors for dependency tracking.

    Every IMAP science data product has its data descriptor.
    TODO: Include all valid science data descriptors from
    imap_data_access once it's defined.

    Here, we add descriptors related to SPICE and other data types.
    Valid data descriptors for SPICE and other data types are:
        1. predict - Predicted data
        2. historical - Historical data
        3. reconstruct - Reconstructed data
        4. nominal - Nominal data
        5. best - BEST will be used to decide if metakernels
                  will include predict or reconstruct kernels
                  if historical kernels are not available.
    """

    PREDICT: str = "predict"
    HISTORICAL: str = "historical"
    RECONSTRUCT: str = "reconstruct"
    NOMINAL: str = "nominal"
    BEST: str = "best"

    @property
    def valid_descriptor(self) -> list[str]:
        """Add data descriptors.

        Returns
        -------
        list[str]
            list of valid data descriptors.
        """
        return [
            self.PREDICT,
            self.HISTORICAL,
            self.RECONSTRUCT,
            self.NOMINAL,
            self.BEST,
        ]


@dataclass
class Relationship:
    """Valid data relationships for dependency tracking.

    Valid data relationships are:
        1. HARD - the data is required for the pipeline to run
        2. SOFT - the data is optional for the pipeline to run
    """

    HARD: str = "HARD"
    SOFT: str = "SOFT"

    @property
    def valid_relationship(self) -> list[str]:
        """Add data relationships.

        Returns
        -------
        list[str]
            list of valid data relationships.
        """
        return [self.HARD, self.SOFT]


@dataclass
class DependencyType:
    """Valid data dependency type for dependency tracking.

    Valid data dependency types are:
        1. UPSTREAM - Processed product to start current product's process
        2. DOWNSTREAM - future file that needs current file to start its process
    """

    UPSTREAM: str = "UPSTREAM"
    DOWNSTREAM: str = "DOWNSTREAM"

    @property
    def valid_dependency_type(self) -> list[str]:
        """Add data dependency types.

        Returns
        -------
        list[str]
            list of valid data dependency types.
        """
        return [self.UPSTREAM, self.DOWNSTREAM]


class DependencyConfig:
    """Dependency configuration for IMAP Products.

    We can keep track of dependencies by tracking nodes in a graph. Each node
    represents a data product and the edges represent the dependencies between
    them. There is an upstream/downstream relationship between nodes. A node
    can be any data product, from a science file (instrument, data level, descriptor),
    a SPICE file, or an ancillary file.

    For example, dependency can be accessed like this:
        dependencies["HARD"]["DOWNSTREAM"][('hit', 'l0', 'raw')]
        where ('hit', 'l0', 'raw') is the parent node.

        Example output of above call:
            [('hit', 'l1a', 'all'), ('hit', 'l1b', 'hk')]
    """

    def __init__(self):
        """Read dependency configuration from dependency_config.csv."""
        self.data_source = DataSource()
        self.data_type = DataType()
        self.data_descriptor = DataDescriptor()
        self.relationship = Relationship()
        self.dependency_type = DependencyType()
        self.dependencies = self._load_dependencies()

    def _load_dependencies(self) -> dict:
        """Load dependencies from dependency_config.csv.

        Returns
        -------
        dict
            dictionary of dependencies.
        """
        dependencies = {
            hard_soft: {
                up_down: defaultdict(list)
                for up_down in self.dependency_type.valid_dependency_type
            }
            for hard_soft in self.relationship.valid_relationship
        }

        with open(Path(__file__).parent / "dependency_config.csv") as f:
            for line in f:
                # NOTE: remove extra ',,,,,,,' if you edited the csv file in excel.
                if len(line) <= 1 or line.startswith("#"):
                    # Skip empty lines and comments
                    continue
                contents = line.strip().replace(", ", ",").split(",")
                header = [
                    "primary_source",
                    "primary_data_type",
                    "primary_descriptor",
                    "dependent_source",
                    "dependent_data_type",
                    "dependent_descriptor",
                    "relationship",
                    "dependency_type",
                ]

                if len(contents) != 8:
                    raise ValueError(
                        f"Each dependency shoud have {header}\nCurrent line: {line}"
                    )

                # data_source, data_type, descriptor
                parent_node = tuple(contents[:3])
                child_node = tuple(contents[3:6])

                # validate node
                if not self._validate_node(parent_node) or not self._validate_node(
                    child_node
                ):
                    logger.debug(
                        f"Parent node: {parent_node}, Child node: {child_node}"
                    )
                    raise ValueError(
                        "Data product must have: (source, type, descriptor)"
                    )

                hard_soft = contents[6]
                # Downstream direction
                dependencies[hard_soft][self.dependency_type.DOWNSTREAM][
                    parent_node
                ].append(child_node)
                # Upstream direction (flip parent/child)
                dependencies[hard_soft][self.dependency_type.UPSTREAM][
                    child_node
                ].append(parent_node)

        return dependencies

    def _validate_node(self, node: tuple) -> bool:
        """Validate node.

        Parameters
        ----------
        node : tuple
            Node to validate.

        Returns
        -------
        bool
            True if node is valid, False otherwise.
        """
        if len(node) != 3:
            logger.debug("Missing data source, data type, or descriptor")
            return False
        if node[0] not in self.data_source.valid_source:
            logger.debug(f"Invalid data source: {node[0]}")
            return False
        if node[1] not in self.data_type.valid_type:
            logger.debug(f"Invalid data type: {node[1]}")
            return False
        # TODO: Add descriptor validation once we define all data product's
        # data descriptor.
        return True


def get_dependencies(node, dependency_type, relationship):
    """Lookup the dependencies for the given ``node``.

    A ``node`` is an identifier of the data product, which can be an
    (data_source, data_type, descriptor) tuple, science file identifiers,
    or SPICE file identifiers, or ancillary data file identifiers.

    Parameters
    ----------
    node : tuple
        Quantities that uniquely identify a data product.
    dependency_type : str
        Whether it's UPSTREAM or DOWNSTREAM dependency.
    relationship : str
        Whether it's HARD or SOFT dependency.
        HARD means data is required for pipeline and SOFT
        means data is optional for pipeline.

    Returns
    -------
    dependencies : list
        List of dictionary containing the dependency information.
    """
    # Load the dependencies
    try:
        dependency_config = DependencyConfig()
    except Exception as e:
        logger.error(f"Error loading dependencies: {e!s}")
        return None

    dependencies = dependency_config.dependencies[relationship][dependency_type].get(
        node, []
    )
    # Add keys for a dict-like representation
    dependencies = [
        {"data_source": dep[0], "data_type": dep[1], "descriptor": dep[2]}
        for dep in dependencies
    ]

    return dependencies


def lambda_handler(event, context):
    """Lambda handler for dependency tracking.

    TODO: Create a Lambda function that will be triggered by API Gateway.
    See https://github.com/IMAP-Science-Operations-Center/sds-data-manager/issues/419
    for more details.

    Parameters
    ----------
    event : dict
        If dependency is requested, event input will be:
            {
                "data_source": "hit",
                "data_type": "l0",
                "descriptor": "raw",
                "dependency_type": "UPSTREAM",
                "relationship": "HARD",
            }

    context : dict
        Context dictionary.

    Returns
    -------
    dependencies : list of dict
        statusCode and body containing list of dictionary containing
        the dependencies information like this:
            [
                {
                    "data_source": "hit",
                    "data_type": "l1a",
                    "descriptor": "all",
                },
                {
                    "data_source": "hit",
                    "data_type": "l1b",
                    "descriptor": "hk",
                },
                {
                    "data_source": "sc_attitude",
                    "data_type": "spice",
                    "descriptor": "historical",
                },
            ]
    """
    logger.info(f"Event: {event}")

    dependencies = get_dependencies(
        (event["data_source"], event["data_type"], event["descriptor"]),
        event["dependency_type"],
        event["relationship"],
    )

    if dependencies is None:
        return {
            "statusCode": 500,
            "body": "Failed to load dependencies",
        }

    # TODO: add reprocessing dependencies are handled here
    return {
        "statusCode": 200,
        "body": json.dumps(dependencies),
    }
