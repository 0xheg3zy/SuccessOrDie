import argparse
import asyncio

from .config import (
    DEFAULT_COLLECTION_PATH,
    DEFAULT_ENVIRONMENT_PATH,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    DEFAULT_REPORT_PATH,
    DEFAULT_REQUEST_TIMEOUT
)

from .dependency import (
    build_dependency_graph,
    print_dependency_graph
)

from .executor import (
    execute_test
)

from .llm import (
    generate_test_plan
)

from .parser import (
    extract_collection_variables,
    extract_requests,
    load_collection,
    load_environment
)

from .reporter import (
    print_summary,
    save_report
)

from .state import (
    StateManager
)


def parse_args():

    parser = argparse.ArgumentParser(

        description=(
            "AI-powered API testing tool "
            "for Postman collections"
        )

    )

    parser.add_argument(

        "--collection",

        default=
            DEFAULT_COLLECTION_PATH,

        help=(
            "Path to Postman collection"
        )

    )

    parser.add_argument(

        "--environment",

        default=
            DEFAULT_ENVIRONMENT_PATH,

        help=(
            "Path to Postman environment"
        )

    )

    parser.add_argument(

        "--proxy",

        default=None,

        help=(
            "HTTP proxy. "
            "Example: 127.0.0.1:8080"
        )

    )

    parser.add_argument(

        "--verify",

        type=str,

        default="true",

        choices=[
            "true",
            "false"
        ],

        help=(
            "Verify TLS certificates. "
            "Use false when using Burp "
            "HTTPS interception."
        )

    )

    parser.add_argument(

        "--ollama-url",

        default=
            DEFAULT_OLLAMA_URL,

        help=(
            "Ollama API URL"
        )

    )

    parser.add_argument(

        "--model",

        default=
            DEFAULT_OLLAMA_MODEL,

        help=(
            "Ollama model"
        )

    )

    parser.add_argument(

        "--timeout",

        type=int,

        default=
            DEFAULT_REQUEST_TIMEOUT,

        help=(
            "HTTP request timeout"
        )

    )

    parser.add_argument(

        "--report",

        default=
            DEFAULT_REPORT_PATH,

        help=(
            "Output report path"
        )

    )

    return parser.parse_args()


def normalize_proxy(
    proxy: str | None
):

    if not proxy:

        return None

    if proxy.startswith(
        "http://"
    ):

        return proxy

    if proxy.startswith(
        "https://"
    ):

        return proxy

    return (
        f"http://{proxy}"
    )


async def main():

    args = parse_args()

    proxy = normalize_proxy(
        args.proxy
    )

    verify_tls = (

        args.verify.lower()

        ==

        "true"

    )

    print(
        "[+] AI API Tester"
    )

    print(
        f"[+] Collection: "
        f"{args.collection}"
    )

    if args.environment:

        print(
            f"[+] Environment: "
            f"{args.environment}"
        )

    if proxy:

        print(
            f"[+] Proxy enabled: "
            f"{proxy}"
        )

    else:

        print(
            "[+] Proxy disabled"
        )

    print(
        f"[+] TLS verification: "
        f"{verify_tls}"
    )

    print(
        f"[+] Ollama model: "
        f"{args.model}"
    )

    print(
        "\n[+] Loading collection..."
    )

    collection = load_collection(

        args.collection

    )

    collection_variables = (
        extract_collection_variables(

            collection

        )
    )

    environment_variables = (
        load_environment(

            args.environment

        )
    )

    static_variables = {}

    # Collection variables

    static_variables.update(

        collection_variables

    )

    # Environment variables override
    # collection variables

    static_variables.update(

        environment_variables

    )

    state = StateManager(

        static_variables

    )

    print(
        f"[+] Static variables: "
        f"{len(static_variables)}"
    )

    requests = extract_requests(

        collection

    )

    print(
        f"[+] API requests: "
        f"{len(requests)}"
    )

    dependency_graph = (
        build_dependency_graph(

            requests

        )
    )

    print_dependency_graph(

        dependency_graph

    )

    results = []

    for index, api_request in enumerate(

        requests,

        start=1

    ):

        print(

            "\n"
            f"[{index}/{len(requests)}] "
            f"{api_request.method} "
            f"{api_request.url}"

        )

        try:

            test_plan = (

                await generate_test_plan(

                    api_request,

                    model=
                        args.model,

                    ollama_url=
                        args.ollama_url

                )

            )

        except Exception as error:

            print(

                "[!] LLM error: "

                f"{error}"

            )

            continue

        print(

            f"[+] Generated "
            f"{len(test_plan.tests)} "
            f"tests"

        )

        for test in (

            test_plan.tests

        ):

            print(

                f"    -> "
                f"{test.name}"

            )

            try:

                result = (

                    await execute_test(

                        test,

                        state,

                        proxy=
                            proxy,

                        timeout=
                            args.timeout,

                        verify=
                            verify_tls

                    )

                )

                results.append(

                    result

                )

                status = (

                    "PASS"

                    if result[
                        "passed"
                    ]

                    else

                    "FAIL"

                )

                print(

                    f"       "
                    f"{result['response']['status_code']} "
                    f"{status}"

                )

                if result[
                    "extracted"
                ]:

                    print(

                        "       "
                        f"Extracted: "
                        f"{result['extracted']}"

                    )

            except Exception as error:

                print(

                    "       "
                    "[!] Execution error: "

                    f"{error}"

                )

    save_report(

        results,

        args.report

    )

    print_summary(

        results

    )

    print(

        f"[+] Report saved to "
        f"{args.report}"

    )


if __name__ == "__main__":

    asyncio.run(

        main()

    )