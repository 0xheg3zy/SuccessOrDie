import json

import httpx

from .config import (
    OLLAMA_MODEL,
    OLLAMA_URL
)

from .models import (
    APIRequest,
    TestPlan
)


SYSTEM_PROMPT = """
You are an expert API security tester.

Your job is to analyze an API endpoint
and generate a structured API testing plan.

Focus on:

- Functional testing
- Missing parameters
- Invalid parameters
- Boundary testing
- Authentication
- Authorization
- BOLA / IDOR
- Rate limiting
- Information disclosure
- HTTP method validation

Important rules:

1. Return ONLY valid JSON.
2. Do not return markdown.
3. Do not invent authentication tokens.
4. Use the original endpoint URL.
5. Keep tests practical.
6. Every test must contain expected_status_codes.
7. Use extractors when a successful response
   contains useful values such as:
   token
   access_token
   id
   user_id
   order_id

Expected JSON format:

{
  "endpoint": "string",
  "method": "string",
  "tests": [
    {
      "name": "string",
      "category": "string",
      "description": "string",
      "request": {
        "method": "GET",
        "url": "string",
        "headers": {},
        "params": {},
        "body": null
      },
      "expected_status_codes": [200],
      "extractors": [
        {
          "name": "token",
          "json_path": "data.token"
        }
      ]
    }
  ]
}
"""


async def generate_test_plan(
    api_request: APIRequest
):

    prompt = f"""
Analyze this API endpoint.

Endpoint:

{json.dumps(
    api_request.model_dump(),
    indent=2
)}

Generate a practical API test plan.

If the endpoint is a login endpoint,
generate a valid authentication test
and extract a token if the response
contains one.

If the endpoint contains an object ID,
consider authorization testing.

Return ONLY JSON.
"""

    payload = {

        "model":
            OLLAMA_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    prompt
            }

        ],

        "stream":
            False,

        "format":
            "json"
    }

    async with httpx.AsyncClient(
        timeout=120
    ) as client:

        response = await client.post(

            OLLAMA_URL,

            json=payload
        )

        response.raise_for_status()

        data = response.json()

    content = data[
        "message"
    ][
        "content"
    ]

    return TestPlan.model_validate_json(
        content
    )