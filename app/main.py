import asyncio

from .config import (
    COLLECTION_PATH,
    REPORT_PATH
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
    extract_requests,
    extract_variables,
    load_collection
)

from .reporter import (
    print_summary,
    save_report
)

from .state import (
    StateManager
)


async def main():

    print(
        "[+] Loading Postman collection..."
    )

    collection = load_collection(
        COLLECTION_PATH
    )

    variables = extract_variables(
        collection
    )

    print(
        f"[+] Found "
        f"{len(variables)} "
        f"collection variables"
    )

    state = StateManager(
        variables
    )

    requests = extract_requests(
        collection
    )

    print(
        f"[+] Found "
        f"{len(requests)} "
        f"API requests"
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
                    api_request
                )
            )

        except Exception as error:

            print(
                "[!] LLM error:"
                f" {error}"
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
                        state
                    )
                )

                results.append(
                    result
                )

                status = (

                    "PASS"

                    if result["passed"]

                    else "FAIL"

                )

                print(
                    f"       "
                    f"{result['response']['status_code']} "
                    f"{status}"
                )

                if result["extracted"]:

                    print(
                        "       "
                        f"Extracted: "
                        f"{result['extracted']}"
                    )

            except Exception as error:

                print(
                    "       "
                    f"[!] Execution error: "
                    f"{error}"
                )

    save_report(

        results,

        REPORT_PATH
    )

    print_summary(
        results
    )

    print(
        f"[+] Report saved to "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )