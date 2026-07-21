import re


VARIABLE_PATTERN = re.compile(
    r"\{\{\s*([^}]+?)\s*\}\}"
)


def extract_variables_from_value(
    value
):

    if isinstance(
        value,
        str
    ):

        return set(
            VARIABLE_PATTERN.findall(
                value
            )
        )

    if isinstance(
        value,
        dict
    ):

        result = set()

        for val in value.values():

            result.update(
                extract_variables_from_value(
                    val
                )
            )

        return result

    if isinstance(
        value,
        list
    ):

        result = set()

        for item in value:

            result.update(
                extract_variables_from_value(
                    item
                )
            )

        return result

    return set()


def build_dependency_graph(
    requests
):

    graph = {}

    for request in requests:

        dependencies = set()

        dependencies.update(
            extract_variables_from_value(
                request.url
            )
        )

        dependencies.update(
            extract_variables_from_value(
                request.headers
            )
        )

        dependencies.update(
            extract_variables_from_value(
                request.params
            )
        )

        dependencies.update(
            extract_variables_from_value(
                request.body
            )
        )

        graph[
            request.name
        ] = list(
            dependencies
        )

    return graph


def print_dependency_graph(
    graph
):

    print(
        "\n========== DEPENDENCY GRAPH =========="
    )

    for endpoint, dependencies in graph.items():

        if dependencies:

            print(
                f"{endpoint}"
                f" -> "
                f"{', '.join(dependencies)}"
            )

        else:

            print(
                f"{endpoint}"
                f" -> "
                f"no dependencies"
            )

    print(
        "=======================================\n"
    )