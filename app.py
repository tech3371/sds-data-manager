#!/usr/bin/env python3
import os
import boto3 
import string
import random
import aws_cdk as cdk
import aws_cdk.assertions as assertions
from sds_in_a_box.sds_in_a_box_stack import SdsInABoxStack

random_name = "".join( [random.choice(string.ascii_lowercase) for i in range(8)] )

app = cdk.App()
SdsInABoxStack(app, "SdsInABoxStack-"+random_name, random_letters=random_name)

app.synth()

#app = cdk.App()
#stack = SdsInABoxStack(app, "sds-in-a-box")
#template = assertions.Template.from_stack(stack)
#print(template)