#!/usr/bin/env python3
import os
import aws_cdk as cdk

from cdk_stack import RedFlagCIStack

app = cdk.App()

# Entrypoint that instantiates RedFlagCIStack in region ap-south-1
RedFlagCIStack(
    app, "RedFlagCIStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT", os.environ.get("AWS_ACCOUNT_ID")),
        region="ap-south-1"
    )
)

app.synth()
