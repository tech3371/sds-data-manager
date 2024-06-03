"""Stores the downstream and upstream dependency configuration of some IMAP instruments.

This is used to populate pre-processing dependency table in the database.

NOTE: This setup assumes that we get one data file with multiple APIDs data.
This is why we have only one dependency for l0. We expect that we get one
l0 file, eg. imap_idex_l0_raw_20240529_v001.pkts, which contains all the data of all
APIDs. That l0 data file will kick off one l1a process for 'all' as l1a will produce
multiple files with different descriptor(aka different data product per APID). Those
different descriptor are handled by CDF attrs.
"""

from .database.models import PreProcessingDependency

# TODO: revisit this after SIT-3
# Instruments name in alphabetic order and dependency is added in this order
# codice
# glows
# hi
# hit
# idex
# lo
# mag
# swapi
# swe
# ultra


downstream_dependents = [
    # <---- CoDICE Dependencies ---->
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
    # CoDICE l1a to l1b
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
    # <---- GLOWS Dependencies ---->
    # TODO: add GLOWS l0 to l1a dependencies
    # <---- HI Dependencies ---->
    PreProcessingDependency(
        primary_instrument="hi",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="hi",
        dependent_data_level="l1a",
        dependent_descriptor="all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="hi",
        primary_data_level="l1a",
        primary_descriptor="45sensor-histogram",
        dependent_instrument="hi",
        dependent_data_level="l1b",
        dependent_descriptor="45sensor-histogram",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="hi",
        primary_data_level="l1a",
        primary_descriptor="45sensor-de",
        dependent_instrument="hi",
        dependent_data_level="l1b",
        dependent_descriptor="45sensor-de",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="hi",
        primary_data_level="l1a",
        primary_descriptor="45sensor-hk",
        dependent_instrument="hi",
        dependent_data_level="l1b",
        dependent_descriptor="45sensor-hk",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="hi",
        primary_data_level="l1b",
        primary_descriptor="45sensor-de",
        dependent_instrument="hi",
        dependent_data_level="l1c",
        dependent_descriptor="45sensor-pset",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # TODO: add IMAP-Hi 90 sensor data products
    # <---- HIT Dependencies ---->
    PreProcessingDependency(
        primary_instrument="hit",
        primary_data_level="l0",
        primary_descriptor="sci",
        dependent_instrument="hit",
        dependent_data_level="l1a",
        dependent_descriptor="sci",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="hit",
        primary_data_level="l1a",
        primary_descriptor="sci",
        dependent_instrument="hit",
        dependent_data_level="l1b",
        dependent_descriptor="sci",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- IDEX Dependencies ---->
    PreProcessingDependency(
        primary_instrument="idex",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="idex",
        dependent_data_level="l1",
        dependent_descriptor="sci",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- LO Dependencies ---->
    # TODO: add LO dependencies
    PreProcessingDependency(
        primary_instrument="lo",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="lo",
        dependent_data_level="l1a",
        dependent_descriptor="all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="lo",
        primary_data_level="l1a",
        primary_descriptor="histogram",
        dependent_instrument="lo",
        dependent_data_level="l1b",
        dependent_descriptor="histogram",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- MAG Dependencies ---->
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="mag",
        dependent_data_level="l1a",
        dependent_descriptor="all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1a",
        primary_descriptor="normal-mago",
        dependent_instrument="mag",
        dependent_data_level="l1b",
        dependent_descriptor="normal-mago",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1a",
        primary_descriptor="normal-magi",
        dependent_instrument="mag",
        dependent_data_level="l1b",
        dependent_descriptor="normal-magi",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1a",
        primary_descriptor="burst-mago",
        dependent_instrument="mag",
        dependent_data_level="l1b",
        dependent_descriptor="burst-mago",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1a",
        primary_descriptor="burst-magi",
        dependent_instrument="mag",
        dependent_data_level="l1b",
        dependent_descriptor="burst-magi",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1b",
        primary_descriptor="normal-mago",
        dependent_instrument="mag",
        dependent_data_level="l1c",
        dependent_descriptor="normal-mago",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1b",
        primary_descriptor="normal-magi",
        dependent_instrument="mag",
        dependent_data_level="l1c",
        dependent_descriptor="normal-magi",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1b",
        primary_descriptor="burst-mago",
        dependent_instrument="mag",
        dependent_data_level="l1c",
        dependent_descriptor="burst-mago",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="mag",
        primary_data_level="l1b",
        primary_descriptor="burst-magi",
        dependent_instrument="mag",
        dependent_data_level="l1c",
        dependent_descriptor="burst-magi",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- SWAPI Dependencies ---->
    PreProcessingDependency(
        primary_instrument="swapi",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="swapi",
        dependent_data_level="l1",
        dependent_descriptor="all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- SWE Dependencies ---->
    PreProcessingDependency(
        primary_instrument="swe",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="swe",
        dependent_data_level="l1a",
        dependent_descriptor="sci",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="swe",
        primary_data_level="l1a",
        primary_descriptor="sci",
        dependent_instrument="swe",
        dependent_data_level="l1b",
        dependent_descriptor="sci",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # <---- ULTRA Dependencies ---->
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l0",
        primary_descriptor="raw",
        dependent_instrument="ultra",
        dependent_data_level="l1a",
        dependent_descriptor="all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # Ultra-45 products
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="45sensor-de",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="45sensor-histogram",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="45sensor-aux",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="45sensor-rates",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # TODO: uncomment for post-SIT-3
    # PreProcessingDependency(
    #     primary_instrument="codice",
    #     primary_data_level="l2",
    #     primary_descriptor="todo",
    #     dependent_instrument="ultra",
    #     dependent_data_level="l1b",
    #     dependent_descriptor="45all",
    #     relationship="HARD",
    #     direction="DOWNSTREAM",
    # ),
    # PreProcessingDependency(
    #     primary_instrument="swapi",
    #     primary_data_level="l2",
    #     primary_descriptor="todo",
    #     dependent_instrument="ultra",
    #     dependent_data_level="l1b",
    #     dependent_descriptor="45all",
    #     relationship="HARD",
    #     direction="DOWNSTREAM",
    # ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="45sensor-de",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="45sensor-extendedspin",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="45sensor-cullingmask",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="45sensor-badtimes",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="45all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # Ultra-90 products
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="90sensor-de",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="90sensor-histogram",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="90sensor-aux",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1a",
        primary_descriptor="90sensor-rates",
        dependent_instrument="ultra",
        dependent_data_level="l1b",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    # TODO: uncomment for post-SIT-3
    # PreProcessingDependency(
    #     primary_instrument="codice",
    #     primary_data_level="l2",
    #     primary_descriptor="todo",
    #     dependent_instrument="ultra",
    #     dependent_data_level="l1b",
    #     dependent_descriptor="90all",
    #     relationship="HARD",
    #     direction="DOWNSTREAM",
    # ),
    # PreProcessingDependency(
    #     primary_instrument="swapi",
    #     primary_data_level="l2",
    #     primary_descriptor="todo",
    #     dependent_instrument="ultra",
    #     dependent_data_level="l1b",
    #     dependent_descriptor="90all",
    #     relationship="HARD",
    #     direction="DOWNSTREAM",
    # ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="90sensor-de",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="90sensor-extendedspin",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="90sensor-cullingmask",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
    PreProcessingDependency(
        primary_instrument="ultra",
        primary_data_level="l1b",
        primary_descriptor="90sensor-badtimes",
        dependent_instrument="ultra",
        dependent_data_level="l1c",
        dependent_descriptor="90all",
        relationship="HARD",
        direction="DOWNSTREAM",
    ),
]

upstream_dependents = [dep.reverse_direction() for dep in downstream_dependents]

all_dependents = downstream_dependents + upstream_dependents
