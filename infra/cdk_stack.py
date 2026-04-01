from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_sns as sns,
    aws_logs as logs,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class RedFlagCIStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function: name="redflagci-scanner", Python 3.12, 1024MB memory, 5 minute timeout
        scanner_lambda = _lambda.Function(
            self, "ScannerFunction",
            function_name="redflagci-scanner",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("../backend"),
            handler="handler.lambda_handler",
            memory_size=1024,
            timeout=Duration.minutes(5)
        )

        # API Gateway HTTP API
        http_api = apigw.HttpApi(
            self, "WebhookApi",
            api_name="redflagci-webhook-api"
        )
        
        lambda_integration = integrations.HttpLambdaIntegration(
            "WebhookIntegration",
            scanner_lambda
        )

        http_api.add_routes(
            path="/webhook",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration
        )

        # DynamoDB table: name="redflagci-scans", partition key=repo_id (String), sort key=pr_number_timestamp (String)
        scans_table = dynamodb.Table(
            self, "ScansTable",
            table_name="redflagci-scans",
            partition_key=dynamodb.Attribute(name="repo_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="pr_number_timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY  # Can be adjusted for production
        )
        
        scans_table.add_global_secondary_index(
            index_name="RepoIdIndex",
            partition_key=dynamodb.Attribute(name="repo_id", type=dynamodb.AttributeType.STRING)
        )

        # S3 bucket: name="redflagci-reports-{account_id}", versioning enabled, lifecycle rule
        reports_bucket = s3.Bucket(
            self, "ReportsBucket",
            bucket_name=f"redflagci-reports-{self.account}",
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    expiration=Duration.days(90)
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )

        # Secrets Manager secret: name="redflag/github-app"
        github_app_secret = secretsmanager.Secret(
            self, "GitHubAppSecret",
            secret_name="redflag/github-app",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template="{}",
                generate_string_key="GITHUB_APP_ID"
            )
        )

        # SNS topic: name="redflag-critical-alerts"
        alerts_topic = sns.Topic(
            self, "CriticalAlertsTopic",
            topic_name="redflag-critical-alerts"
        )

        # CloudWatch log group: name="/aws/lambda/redflagci-scanner", retention 30 days
        lambda_log_group = logs.LogGroup(
            self, "ScannerLambdaLogGroup",
            log_group_name=f"/aws/lambda/{scanner_lambda.function_name}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Output declarations
        CfnOutput(self, "ApiGatewayUrl", value=http_api.url, description="API_GATEWAY_URL")
        CfnOutput(self, "LambdaFunctionName", value=scanner_lambda.function_name, description="LAMBDA_FUNCTION_NAME")
        CfnOutput(self, "DynamoDbTableName", value=scans_table.table_name, description="DYNAMODB_TABLE_NAME")
        CfnOutput(self, "S3BucketName", value=reports_bucket.bucket_name, description="S3_BUCKET_NAME")
        CfnOutput(self, "SnsTopicArn", value=alerts_topic.topic_arn, description="SNS_TOPIC_ARN")
        CfnOutput(self, "AwsRegion", value=self.region, description="AWS_REGION")
