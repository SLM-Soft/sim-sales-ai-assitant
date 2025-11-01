import os
import json


def handler(event, context):
    """
    Health check endpoint for Netlify Functions.
    Returns configuration status without calling AWS Bedrock.
    """
    # Load environment variables
    aws_region = os.getenv("AWS_REGION", "eu-central-1")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")
    use_mock = os.getenv("USE_MOCK_BEDROCK", "false").lower() in ("1", "true", "yes")

    response_body = {
        "ok": True,
        "region": aws_region,
        "model": model_id,
        "mock": use_mock
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Configure appropriately for production
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(response_body)
    }
