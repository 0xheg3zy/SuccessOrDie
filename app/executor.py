import httpx

from .config import (
    REQUEST_TIMEOUT
)

from .models import (
    TestCase
)

from .resolver import (
    resolve_recursive
)

from .state import (
    StateManager,
    extract_json_value
)


async def execute_test(
    test_case: TestCase,
    state: StateManager
):

    request = test_case.request

    url = resolve_recursive(
        request.url,
        state
    )

    headers = resolve_recursive(
        request.headers,
        state
    )

    params = resolve_recursive(
        request.params,
        state
    )

    body = resolve_recursive(
        request.body,
        state
    )

    async with httpx.AsyncClient(

        timeout=
            REQUEST_TIMEOUT,

        follow_redirects=
            True

    ) as client:

        response = await client.request(

            method=
                request.method,

            url=
                url,

            headers=
                headers,

            params=
                params,

            json=
                body
        )

    try:

        response_json = (
            response.json()
        )

    except Exception:

        response_json = None

    extracted = {}

    if response_json:

        for extractor in (
            test_case.extractors
        ):

            value = extract_json_value(

                response_json,

                extractor.json_path
            )

            if value is not None:

                state.set(

                    extractor.name,

                    value
                )

                extracted[
                    extractor.name
                ] = value

    passed = (

        response.status_code

        in test_case.expected_status_codes

    )

    return {

        "test_name":
            test_case.name,

        "category":
            test_case.category,

        "description":
            test_case.description,

        "request": {

            "method":
                request.method,

            "url":
                url,

            "headers":
                headers,

            "body":
                body
        },

        "response": {

            "status_code":
                response.status_code,

            "headers":
                dict(
                    response.headers
                ),

            "body":
                response.text[
                    :5000
                ]
        },

        "expected_status_codes":
            test_case.expected_status_codes,

        "extracted":
            extracted,

        "state":
            state.all(),

        "passed":
            passed
    }