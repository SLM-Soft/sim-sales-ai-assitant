import os
import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

# Setup logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("bedrock-function")

# Configuration from environment variables
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")
USE_MOCK = os.getenv("USE_MOCK_BEDROCK", "false").lower() in ("1", "true", "yes")

# Initialize boto3 client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def extract_text_from_bedrock_response(response):
    """
    Extracts text from boto3 invoke_model response.
    Returns a string (empty if extraction fails).
    """
    raw_bytes = b""

    body = response.get("body") if isinstance(response, dict) else None

    try:
        if hasattr(body, "read"):
            raw_bytes = body.read()
        elif isinstance(body, (bytes, bytearray)):
            raw_bytes = bytes(body)
        elif body is None:
            raw_bytes = json.dumps(response).encode("utf-8")
        else:
            raw_bytes = str(body).encode("utf-8")
    except Exception as e:
        LOG.exception("Error while reading response body: %s", e)
        raw_bytes = str(response).encode("utf-8")

    try:
        text = raw_bytes.decode("utf-8")
    except Exception:
        text = repr(raw_bytes)

    return text


def handler(event, context):
    """
    Main Bedrock endpoint: accepts message list, formats prompt, and calls Bedrock.
    Returns text response in the `output` field.
    """
    # Parse request body
    try:
        if event.get("body"):
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = {}
    except json.JSONDecodeError as e:
        LOG.error("Invalid JSON in request body: %s", e)
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"success": False, "output": "Invalid JSON in request body"})
        }

    # Handle OPTIONS request for CORS
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }

    # Extract parameters
    messages = body.get("messages", [])
    max_tokens = body.get("maxTokens", 1024)
    temperature = body.get("temperature", 0.7)

    # Mock mode for development
    if USE_MOCK:
        LOG.info("USE_MOCK_BEDROCK is enabled — returning mock response.")
        prompt_preview = " | ".join(f"{m.get('role')}:{m.get('content')}" for m in messages)
        mock_text = f"[MOCK] Response to prompt: {prompt_preview[:300]}"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"success": True, "output": mock_text})
        }

    # Format prompt from messages
    prompt_parts = [f"{m.get('role', 'User')}: {m.get('content', '')}" for m in messages]
    prompt = "\n".join(prompt_parts) + "\nAssistant:"

    # Build request body for Bedrock
    bedrock_body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": int(max_tokens),
            "temperature": float(temperature),
        },
    }

    try:
        # Check for AWS credentials
        session = boto3.Session()
        if not session.get_credentials():
            LOG.warning("No AWS credentials available when calling bedrock function")
            raise NoCredentialsError()

        LOG.info("Invoking Bedrock model: %s (prompt len=%d)", MODEL_ID, len(prompt))
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            body=json.dumps(bedrock_body).encode("utf-8"),
        )

        raw_text = extract_text_from_bedrock_response(response)
        LOG.debug("Raw response text (first 500 chars): %s", raw_text[:500])

        # Try to parse JSON response
        output = raw_text
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                # Standard variants: parsed.outputs or parsed.generatedText
                if "outputs" in parsed:
                    parts = []
                    for out in parsed.get("outputs", []):
                        for c in out.get("content", []):
                            parts.append(c.get("text") or c.get("body") or "")
                    output = "".join(parts).strip()
                elif "generatedText" in parsed:
                    output = str(parsed.get("generatedText"))
                else:
                    output = json.dumps(parsed)
        except Exception:
            # If not JSON, keep raw text
            output = raw_text

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"success": True, "output": output})
        }

    except NoCredentialsError:
        LOG.exception("Bedrock client error - No AWS credentials")
        return {
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "success": False,
                "output": "AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure AWS CLI."
            })
        }

    except (BotoCoreError, ClientError) as e:
        LOG.exception("Bedrock client error: %s", e)
        return {
            "statusCode": 502,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"success": False, "output": str(e)})
        }

    except Exception as e:
        LOG.exception("Unexpected error in bedrock function: %s", e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"success": False, "output": str(e)})
        }
