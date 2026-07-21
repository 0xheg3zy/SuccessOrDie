import json

import httpx

from .config import (
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL
)

from .models import (
    APIRequest,
    TestPlan
)


SYSTEM_PROMPT = """
You are an expert API security tester.

Your job is to analyze API endpoints
and generate structured API testing plans.

Focus on:

1. Functional testing
2. Missing parameters
3. Invalid parameters
4. Boundary testing
5. Authentication
6. Authorization
7. BOLA / IDOR
8. Rate limiting
9. Information disclosure
10. HTTP method validation

Rules:

- Return ONLY valid JSON.
- Do not return markdown.
- Do not invent tokens.
- Use the supplied endpoint.
- Keep tests practical.
- Every test must have expected_status_codes.
- Use extractors when a successful response
  contains useful runtime values.

Useful runtime values include:

- token
- access_token
- refresh_token
- id
- user_id
- order_id
- session_id

Expected JSON:

{
  "endpoint": "string",
  "method": "GET",
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
    api_request: APIRequest,
    model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL
):

    prompt = f"""
Analyze this API endpoint.

Endpoint:

{json.dumps(
    api_request.model_dump(),
    indent=2
)}

Generate a practical API test plan.

If the endpoint is an authentication
endpoint and the response contains a
token, add an extractor.

If the endpoint contains object IDs,
consider authorization testing.

Return ONLY JSON.
"""

    payload = {

        "model":
            model,

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

        timeout=
            DEFAULT_LLM_TIMEOUT

    ) as client:

        response = await client.post(

            ollama_url,

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