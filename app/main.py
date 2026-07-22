import argparse

from .config import (
    DEFAULT_COLLECTION_PATH,
    DEFAULT_ENVIRONMENT_PATH,
    DEFAULT_LLM_TIMEOUT,
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


proxy_copy = None
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
            DEFAULT_COLLECTION_PATH

    )

    parser.add_argument(

        "--environment",

        default=
            DEFAULT_ENVIRONMENT_PATH

    )

    parser.add_argument(

        "--proxy",

        default=None,

        help=(
            "Proxy for target API requests. "
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
            "Verify TLS certificates "
            "for target API requests"
        )

    )

    parser.add_argument(

        "--ollama-url",

        default=
            DEFAULT_OLLAMA_URL

    )

    parser.add_argument(

        "--model",

        default=
            DEFAULT_OLLAMA_MODEL

    )

    parser.add_argument(

        "--timeout",

        type=int,

        default=
            DEFAULT_REQUEST_TIMEOUT,

        help=(
            "Target API timeout"
        )

    )

    parser.add_argument(

        "--llm-timeout",

        type=int,

        default=
            DEFAULT_LLM_TIMEOUT,

        help=(
            "Ollama timeout"
        )

    )

    parser.add_argument(

        "--report",

        default=
            DEFAULT_REPORT_PATH

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


def main():

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
        "[+] Collection: "
        f"{args.collection}"
    )

    print(
        "[+] Environment: "
        f"{args.environment}"
    )

    print(
        "[+] Proxy enabled: "
        f"{proxy or 'None'}"
    )

    print(
        "[+] TLS verification: "
        f"{verify_tls}"
    )

    print(
        "[+] Ollama model: "
        f"{args.model}"
    )

    print(
        "[+] Ollama URL: "
        f"{args.ollama_url}"
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

    static_variables.update(

        collection_variables

    )

    static_variables.update(

        environment_variables

    )

    state = StateManager(

        static_variables

    )

    print(
        "[+] Static variables: "
        f"{len(static_variables)}"
    )

    requests_list = extract_requests(

        collection

    )

    print(
        "[+] API requests: "
        f"{len(requests_list)}"
    )

    dependency_graph = (

        build_dependency_graph(

            requests_list

        )

    )

    print_dependency_graph(

        dependency_graph

    )

    results = []

    for index, api_request in enumerate(

        requests_list,

        start=1

    ):

        print(

            "\n"
            f"[{index}/{len(requests_list)}] "
            f"{api_request.method} "
            f"{api_request.url}"

        )

        try:

            test_plan = (

                generate_test_plan(

                    api_request,

                    model=
                        args.model,

                    ollama_url=
                        args.ollama_url,

                    timeout=
                        args.llm_timeout,

                    proxy=
                        proxy,
                        
                    verify=
                        verify_tls

                )

            )

        except Exception as error:

            print(
                "\n[!] LLM error: "
                f"{error}"
            )

            continue

        print(

            f"\n[+] Generated "
            f"{len(test_plan.tests)} tests"

        )

        for test_index, test in enumerate(

            test_plan.tests,

            start=1

        ):

            print(

                f"\n    "
                f"[{test_index}/"
                f"{len(test_plan.tests)}] "
                f"{test.name}"

            )

            try:
                proxy_copy = proxy
                result = execute_test(

                    test,

                    state,

                    proxy=
                        proxy,

                    timeout=
                        args.timeout,

                    verify=
                        verify_tls

                )

                results.append(

                    result

                )

                if result.get(
                    "extracted"
                ):

                    print(

                        "    Extracted: "

                        f"{result['extracted']}"

                    )

            except Exception as error:

                print(

                    "    [!] Execution error: "

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

        "[+] Report saved to "
        f"{args.report}"

    )


if __name__ == "__main__":

    main()