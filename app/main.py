import argparse

from .config import (
    DEFAULT_COLLECTION_PATH,
    DEFAULT_ENVIRONMENT_PATH,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MODEL_STATUS_TIMEOUT,
    DEFAULT_OLLAMA_BASE_URL,
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
    analyze_test_result,
    generate_test_plan
)

from .model_monitor import (
    print_model_status
)

from .parser import (
    extract_collection_variables,
    extract_requests,
    load_collection,
    load_environment
)

from .proxy import (
    ProxySession
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

        description=
            "AI API Testing Tool"

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

        default=None

    )

    parser.add_argument(

        "--verify",

        type=str,

        default="true",

        choices=[
            "true",
            "false"
        ]

    )

    parser.add_argument(

        "--ollama-url",

        default=
            DEFAULT_OLLAMA_URL

    )

    parser.add_argument(

        "--ollama-base-url",

        default=
            DEFAULT_OLLAMA_BASE_URL

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
            DEFAULT_REQUEST_TIMEOUT

    )

    parser.add_argument(

        "--llm-timeout",

        type=int,

        default=
            DEFAULT_LLM_TIMEOUT

    )

    parser.add_argument(

        "--model-status-timeout",

        type=int,

        default=
            DEFAULT_MODEL_STATUS_TIMEOUT

    )

    parser.add_argument(

        "--report",

        default=
            DEFAULT_REPORT_PATH

    )

    return parser.parse_args()


def normalize_proxy(
    proxy
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

        "http://"
        + proxy

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
        f"{proxy or 'Disabled'}"

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

        "[+] LLM traffic proxy: "
        f"{proxy or 'Disabled'}"

    )

    client = ProxySession(

        proxy=
            proxy,

        verify=
            verify_tls

    )

    try:

        print(

            "\n[+] Checking Ollama "
            "model status..."

        )

        print_model_status(

            client,

            base_url=
                args.ollama_base_url,

            model=
                args.model,

            timeout=
                args.model_status_timeout

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

            dependencies = (

                dependency_graph.get(

                    api_request.name,

                    []

                )

            )

            try:

                test_plan = (

                    generate_test_plan(

                        client,

                        api_request,

                        static_variables=
                            state.static_values(),

                        dynamic_variables=
                            state.dynamic_values(),

                        dependencies=
                            dependencies,

                        model=
                            args.model,

                        ollama_url=
                            args.ollama_url,

                        timeout=
                            args.llm_timeout

                    )

                )

            except Exception as error:

                print(

                    "[!] LLM error: "
                    f"{error}"

                )

                continue

            print(

                "[+] Generated "
                f"{len(test_plan.tests)} "
                "tests"

            )

            for test_index, test_case in enumerate(

                test_plan.tests,

                start=1

            ):

                print(

                    "\n"
                    f"    [{test_index}/"
                    f"{len(test_plan.tests)}] "
                    f"{test_case.name}"

                )

                result = execute_test(

                    client,

                    test_case,

                    state,

                    timeout=
                        args.timeout

                )

                if "actual" not in result:

                    results.append(

                        result

                    )

                    continue

                print(

                    "    [AI] "
                    "Analyzing result..."
                )

                try:

                    analysis = (

                        analyze_test_result(

                            client,

                            test_case,

                            result[
                                "actual"
                            ].get(
                                "status_code"
                            ),

                            result[
                                "actual"
                            ].get(
                                "response"
                            ),

                            model=
                                args.model,

                            ollama_url=
                                args.ollama_url,

                            timeout=
                                args.llm_timeout

                        )

                    )

                    result.update(

                        analysis

                    )

                    status = (

                        "PASS"

                        if result.get(
                            "passed"
                        )

                        else

                        "FAIL"

                    )

                    print(

                        f"    [{status}] "
                        f"{result.get('reason', '')}"

                    )

                except Exception as error:

                    result[
                        "passed"
                    ] = False

                    result[
                        "reason"
                    ] = (

                        "AI result analysis "
                        "failed: "

                        f"{error}"

                    )

                results.append(

                    result

                )

        save_report(

            results,

            args.report

        )

        print_summary(

            results

        )

        print(

            "[+] Report saved: "
            f"{args.report}"

        )

    finally:

        client.close()


if __name__ == "__main__":

    main()