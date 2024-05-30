"""Stores the downstream dependency configuration of CoDICE.

This is used to populate pre-processing dependency table in the database.

NOTE: This setup assumes that we get one data file everyday with all
the data of multiple apid. This is why we have only one file for each
l0 and descriptor is raw. And l1a that depends on l0 has 'all' as
descriptor with assumption that l1a could produce multiple files
with different descriptor. Those different descriptor are handle in its own
code in imap_processing repo.
"""

from .database.models import PreProcessingDependency

downstream_dependents = [
    # l0 to l1a
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hskp",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hskp",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-counters-aggregated",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-counters-singles",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-counters-aggregated",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-counters-singles",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-sw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-priority",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-nsw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-priority",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-sw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-angular",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-nsw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-angular",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-sw-species",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-species",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-nsw-species",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-species",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-pha",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-pha",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-pha",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-pha",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-omni",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-omni",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-sectored",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-sectored",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="lo-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-ialirt",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l0",
        primary_descriptor="hi-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-ialirt",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # l1a to l1b
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hskp",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hskp",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-counters-aggregated",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-counters-singles",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-counters-aggregated",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-counters-singles",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-sw-priority",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-nsw-priority",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-sw-angular",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-nsw-angular",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-species",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-sw-species",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-species",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-nsw-species",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-pha",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-pha",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-pha",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-pha",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-omni",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-omni",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-sectored",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-sectored",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="lo-ialirt",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1b",
        dependent_descriptor="hi-ialirt",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
]

upstream_dependents = [
    # l1a from l0
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hskp",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hskp",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-counters-aggregated",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-counters-singles",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-counters-aggregated",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-counters-singles",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-priority",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-sw-priority",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-priority",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-nsw-priority",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-angular",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-sw-angular",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-angular",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-nsw-angular",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-sw-species",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-sw-species",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-nsw-species",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-nsw-species",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-pha",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-pha",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-pha",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-pha",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-omni",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-omni",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-sectored",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-sectored",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="lo-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="lo-ialirt",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1a",
        primary_descriptor="hi-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l0",
        dependent_descriptor="hi-ialirt",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    # l1b from l1a
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hskp",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hskp",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-counters-aggregated",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-counters-singles",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-counters-aggregated",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-counters-aggregated",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-counters-singles",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-counters-singles",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-sw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-priority",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-nsw-priority",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-priority",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-sw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-angular",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-nsw-angular",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-angular",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-sw-species",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-sw-species",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-nsw-species",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-nsw-species",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-pha",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-pha",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-pha",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-pha",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-omni",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-omni",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-sectored",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-sectored",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="lo-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="lo-ialirt",
        relationship="HARD",
        direction="UPSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="codice",
        primary_data_level="l1b",
        primary_descriptor="hi-ialirt",
        dependent_instrument="codice",
        dependent_data_level="l1a",
        dependent_descriptor="hi-ialirt",
        relationship="HARD",
        direction="UPSTREAM",
    ),
]