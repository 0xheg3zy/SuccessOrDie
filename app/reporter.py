import json

from pathlib import Path


def save_report(
    results,
    path
):

    output = Path(
        path
    )

    output.parent.mkdir(

        parents=True,

        exist_ok=True

    )

    with open(

        output,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            results,

            file,

            indent=2,

            ensure_ascii=False,

            default=str

        )


def print_summary(
    results
):

    total = len(
        results
    )

    passed = sum(

        1

        for result
        in results

        if result.get(
            "passed"
        )

    )

    failed = (
        total
        -
        passed
    )

    print(
        "\n========== SUMMARY =========="
    )

    print(
        f"Total : {total}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        "============================="
    )