#!/usr/bin/env python3
import random
import string

import aws_cdk as cdk

from sds_in_a_box.sds_in_a_box_stack import SdsInABoxStack

app = cdk.App()

SDS_ID = app.node.try_get_context("SDSID")

if SDS_ID is None:
    raise ValueError(
        "ERROR: Need to specify an ID to name the stack (ex - production, testing, etc)"
    )
elif SDS_ID == "random":
    # A random unique ID for this particular instance of the SDS
    SDS_ID = "".join([random.choice(string.ascii_lowercase) for i in range(8)])


SdsInABoxStack(app, f"SdsInABoxStack-{SDS_ID}", SDS_ID)
app.synth()
