import json

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
You are a senior API security engineer,
penetration tester, and API test designer.

Your job is to analyze a Postman API request and
generate a high-quality API security and functional
test plan.

Do not generate only happy-path tests.

You must reason about the endpoint, its parameters,
headers, body, authentication, authorization,
business logic, and variables.

==================================================
VARIABLE RESOLUTION
==================================================

The request may contain Postman variables such as:

{{base_url}}
{{access_token}}
{{user_id}}
{{address_id}}

Variables can have two sources:

1. Static variables
2. Dynamic variables extracted from previous
   API responses

Rules:

- Never invent a dynamic variable value.
- Never replace a dynamic variable with a fake value.
- If a variable already exists in the available state,
  preserve it.
- If a variable is required but not available,
  keep the placeholder.
- The executor resolves variables before execution.
- If the endpoint creates a value required later,
  create an extractor.

==================================================
TEST DESIGN
==================================================

Generate meaningful tests covering relevant scenarios.

Consider:

1. Happy Path
2. Missing required fields
3. Empty values
4. Null values
5. Invalid data types
6. Invalid formats
7. Boundary values
8. Minimum length
9. Maximum length
10. Below minimum
11. Above maximum
12. Very long input
13. Special characters
14. Unicode
15. Whitespace
16. Duplicate data
17. Invalid authentication
18. Missing authentication
19. Expired authentication
20. Authorization
21. BOLA / IDOR
22. Horizontal privilege escalation
23. Vertical privilege escalation
24. HTTP method validation
25. Content-Type validation
26. Unexpected parameters
27. Mass assignment
28. Rate limiting
29. Sensitive data exposure
30. Error handling
31. Information disclosure
32. Business logic issues

Only generate tests relevant to the endpoint.

Avoid duplicate or meaningless tests.

==================================================
EXPECTED BEHAVIOR
==================================================

Every test MUST contain:

- expected_status_codes
- expected_behavior
- test_rationale

Do NOT invent actual results.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Expected structure:

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

      "expected_behavior": "What should happen.",

      "test_rationale": "Why this test exists.",

      "extractors": [
        {
          "name": "access_token",
          "json_path": "data.access_token"
        }
      ]
    }
  ]
}
"""


ANALYZER_PROMPT = """
You are analyzing the result of an API test.

Compare:

1. Test description
2. Test rationale
3. Expected behavior
4. Expected status codes
5. Actual HTTP status
6. Actual response

Determine:

- PASS or FAIL
- Actual behavior
- Clear reason
- Security impact
- Severity

Do not mark a test as failed only because the
status code differs.

Determine whether actual API behavior violates
expected behavior.

Return ONLY valid JSON:

{
  "passed": true,
  "actual_behavior": "What actually happened.",
  "reason": "Why the test passed or failed.",
  "security_impact": "None or explain the impact.",
  "severity": "info|low|medium|high|critical"
}
"""


def ollama_chat(
    client,
    messages,
    model,
    ollama_url,
    timeout
):

    payload = {

        "model":
            model,

        "messages":
            messages,

        "stream":
            False,

        "format":
            "json"

    }

    print(

        "[LLM] URL      : "
        f"{ollama_url}"

    )

    print(

        "[LLM] Model    : "
        f"{model}"

    )

    print(

        "[LLM] Proxy    : "
        f"{client.proxy or 'Disabled'}"

    )

    response = client.post(

        ollama_url,

        json=payload,

        timeout=
            timeout

    )

    response.raise_for_status()

    data = response.json()

    content = data.get(
        "message",
        {}
    ).get(
        "content",
        ""
    )

    if not content:

        raise RuntimeError(

            "Ollama returned empty content"

        )

    return content


def generate_test_plan(
    client,
    api_request: APIRequest,
    static_variables=None,
    dynamic_variables=None,
    dependencies=None,
    model=DEFAULT_OLLAMA_MODEL,
    ollama_url=DEFAULT_OLLAMA_URL,
    timeout=DEFAULT_LLM_TIMEOUT
):

    context = {

        "request":
            api_request.model_dump(),

        "static_variables":
            static_variables or {},

        "currently_available_dynamic_variables":
            dynamic_variables or {},

        "endpoint_dependencies":
            dependencies or []

    }

    prompt = f"""
Analyze the following Postman API endpoint.

Context:

{json.dumps(
    context,
    indent=2,
    ensure_ascii=False
)}

Generate a comprehensive API test plan.

Important:

- Preserve Postman variables.
- Use available dynamic variables.
- Do not invent dynamic values.
- Generate meaningful edge cases.
- Generate expected behavior.
- Generate test rationale.
- Create extractors for useful response values.
"""

    content = ollama_chat(

        client,

        messages=[

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

        model=
            model,

        ollama_url=
            ollama_url,

        timeout=
            timeout

    )

    return TestPlan.model_validate_json(
        content
    )


def analyze_test_result(
    client,
    test_case,
    actual_status_code,
    actual_response,
    model=DEFAULT_OLLAMA_MODEL,
    ollama_url=DEFAULT_OLLAMA_URL,
    timeout=DEFAULT_LLM_TIMEOUT
):

    context = {

        "test_name":
            test_case.name,

        "category":
            test_case.category,

        "description":
            test_case.description,

        "test_rationale":
            test_case.test_rationale,

        "expected_status_codes":
            test_case.expected_status_codes,

        "expected_behavior":
            test_case.expected_behavior,

        "actual_status_code":
            actual_status_code,

        "actual_response":
            actual_response

    }

    prompt = f"""
Analyze this API test result.

{json.dumps(
    context,
    indent=2,
    ensure_ascii=False
)}

Determine whether the test passed or failed.

Explain exactly why.

Return ONLY valid JSON.
"""

    content = ollama_chat(

        client,

        messages=[

            {
                "role":
                    "system",

                "content":
                    ANALYZER_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    prompt
            }

        ],

        model=
            model,

        ollama_url=
            ollama_url,

        timeout=
            timeout

    )

    return json.loads(
        content
    )