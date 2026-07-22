from enum import verify
import json
import requests

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

Analyze the supplied API endpoint and
generate a practical API security test plan.

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
- Preserve the original request structure.
- Do not remove required headers unless the test
  specifically targets missing headers.

If a successful response contains useful
runtime values, create extractors.

Useful runtime values:

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
  "method": "string",
  "tests": [
    {
      "name": "string",
      "category": "string",
      "description": "string",
      "request": {
        "method": "string",
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


def generate_test_plan(
    api_request: APIRequest,
    model: str = DEFAULT_OLLAMA_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = DEFAULT_LLM_TIMEOUT,
    proxy: str | None = None,
    verify: bool = True
):

    if proxy:
        proxies = {
            "http":
                proxy,
            "https":
                proxy
        }
    else:
        proxies = None

    request_data = (
        api_request.model_dump()
    )

    prompt = f"""
Analyze this API endpoint.

Original API request:

{json.dumps(
    request_data,
    indent=2,
    ensure_ascii=False
)}

Generate a practical API security
test plan based on this request.

Preserve the original request structure.

If this is an authentication endpoint
and the response may contain a token,
add an extractor.

Return ONLY valid JSON.
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

    print(
        "[LLM] URL: "
        f"{ollama_url}"
    )

    print(
        "[LLM] Model: "
        f"{model}"
    )

    print(
        "[LLM] Sending request..."
    )

    try:

        response = requests.post(

            ollama_url,

            json=payload,

            timeout=timeout,
            verify=verify,
            proxies=proxies

        )

        print(
            "[LLM] HTTP status: "
            f"{response.status_code}"
        )

        response.raise_for_status()

    except requests.Timeout:

        raise RuntimeError(

            "Ollama request timed out "
            f"after {timeout} seconds"

        )

    except requests.RequestException as error:

        raise RuntimeError(

            f"Ollama request failed: "
            f"{error}"

        )

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(

            "Ollama returned invalid JSON"

        )

    if "message" not in data:

        raise RuntimeError(

            "Ollama response does not "
            "contain 'message'"

        )

    content = data[
        "message"
    ].get(
        "content",
        ""
    )

    if not content:

        raise RuntimeError(

            "Ollama returned an empty response"

        )

    print(
        "[LLM] Response received"
    )

    try:

        return TestPlan.model_validate_json(
            content
        )

    except Exception as error:

        print(
            "[LLM] Invalid generated plan:"
        )

        print(
            content
        )

        raise RuntimeError(

            "Failed to parse LLM test plan: "
            f"{error}"

        )