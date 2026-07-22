import requests

from .models import TestCase

from .resolver import (
    resolve_recursive
)

from .state import (
    StateManager,
    extract_json_value
)


def execute_test(
    test_case: TestCase,
    state: StateManager,
    proxy: str | None = None,
    timeout: int = 30,
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

    proxies = None

    if proxy:

        proxies = {

            "http":
                proxy,

            "https":
                proxy

        }

    print(
        "\n[HTTP] Sending request"
    )

    print(
        f"[HTTP] Method: "
        f"{request.method}"
    )

    print(
        f"[HTTP] URL: "
        f"{url}"
    )

    print(
        f"[HTTP] Proxy: "
        f"{proxy or 'None'}"
    )

    print(
        f"[HTTP] Verify TLS: "
        f"{verify}"
    )

    try:

        response = requests.request(

            method=
                request.method,

            url=
                url,

            headers=
                headers,

            params=
                params,

            json=
                body,

            proxies=
                proxies,

            verify=
                verify,

            timeout=
                timeout

        )

    except requests.Timeout:

        return {

            "test_name":
                test_case.name,

            "category":
                test_case.category,

            "description":
                test_case.description,

            "error":
                (
                    f"Request timed out "
                    f"after {timeout} seconds"
                ),

            "passed":
                False

        }

    except requests.RequestException as error:

        return {

            "test_name":
                test_case.name,

            "category":
                test_case.category,

            "description":
                test_case.description,

            "error":
                str(error),

            "passed":
                False

        }

    try:

        response_json = (
            response.json()
        )

    except ValueError:

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

        in

        test_case.expected_status_codes

    )

    print(
        f"[HTTP] Status: "
        f"{response.status_code}"
    )

    print(
        f"[TEST] "
        f"{'PASS' if passed else 'FAIL'}"
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