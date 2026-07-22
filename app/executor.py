from .resolver import (
    resolve_request,
    unresolved_variables
)

from .state import (
    StateManager,
    extract_json_value
)


def execute_test(
    client,
    test_case,
    state: StateManager,
    timeout=30
):

    resolved_request = resolve_request(

        test_case.request,

        state

    )

    unresolved = []

    unresolved.extend(

        unresolved_variables(

            resolved_request[
                "url"
            ],

            state

        )

    )

    unresolved.extend(

        unresolved_variables(

            resolved_request[
                "headers"
            ],

            state

        )

    )

    unresolved.extend(

        unresolved_variables(

            resolved_request[
                "params"
            ],

            state

        )

    )

    unresolved.extend(

        unresolved_variables(

            resolved_request[
                "body"
            ],

            state

        )

    )

    if unresolved:

        return {

            "test_name":
                test_case.name,

            "passed":
                False,

            "error":
                "Unresolved variables",

            "unresolved_variables":
                unresolved

        }

    print(
        "\n[HTTP] Sending request"
    )

    print(

        "[HTTP] "
        f"{resolved_request['method']} "
        f"{resolved_request['url']}"

    )

    print(

        "[HTTP] Proxy: "
        f"{client.proxy or 'Disabled'}"

    )

    try:

        response = client.request(

            method=
                resolved_request[
                    "method"
                ],

            url=
                resolved_request[
                    "url"
                ],

            headers=
                resolved_request[
                    "headers"
                ],

            params=
                resolved_request[
                    "params"
                ],

            json=
                resolved_request[
                    "body"
                ],

            timeout=
                timeout

        )

    except Exception as error:

        return {

            "test_name":
                test_case.name,

            "category":
                test_case.category,

            "expected": {

                "status_codes":
                    test_case.expected_status_codes,

                "behavior":
                    test_case.expected_behavior

            },

            "actual": {

                "error":
                    str(error)

            },

            "passed":
                False,

            "reason":
                (
                    "Request execution failed: "
                    f"{error}"
                )

        }

    try:

        response_json = response.json()

    except ValueError:

        response_json = None

    extracted = {}

    if response_json is not None:

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

                print(

                    "[+] Dynamic variable "
                    f"resolved: "
                    f"{extractor.name}"

                )

    return {

        "test_name":
            test_case.name,

        "category":
            test_case.category,

        "description":
            test_case.description,

        "test_rationale":
            test_case.test_rationale,

        "request": {

            "method":
                resolved_request[
                    "method"
                ],

            "url":
                resolved_request[
                    "url"
                ],

            "headers":
                resolved_request[
                    "headers"
                ],

            "params":
                resolved_request[
                    "params"
                ],

            "body":
                resolved_request[
                    "body"
                ]

        },

        "expected": {

            "status_codes":
                test_case.expected_status_codes,

            "behavior":
                test_case.expected_behavior

        },

        "actual": {

            "status_code":
                response.status_code,

            "response":
                response.text[
                    :5000
                ]

        },

        "extracted":
            extracted

    }