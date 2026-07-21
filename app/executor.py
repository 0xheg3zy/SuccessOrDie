import httpx

from .config import (
    DEFAULT_REQUEST_TIMEOUT
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
    state: StateManager,
    proxy: str | None = None,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
    verify: bool = True
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

    client_kwargs = {

        "timeout":
            timeout,

        "follow_redirects":
            True,

        "verify":
            verify
    }

    if proxy:

        client_kwargs[
            "proxy"
        ] = proxy

    async with httpx.AsyncClient(

        **client_kwargs

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

                state.set_dynamic(

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

            "params":
                params,

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
                response.text[:5000]
        },

        "expected_status_codes":
            test_case.expected_status_codes,

        "extracted":
            extracted,

        "state": {

            "static":
                state.static_values(),

            "dynamic":
                state.dynamic_values()

        },

        "passed":
            passed
    }