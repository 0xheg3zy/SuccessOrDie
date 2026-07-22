import re

from .state import StateManager


VARIABLE_PATTERN = re.compile(
    r"\{\{\s*([^}]+?)\s*\}\}"
)


def extract_variables(
    value
):

    if not isinstance(
        value,
        str
    ):

        return []

    return [

        match.strip()

        for match
        in VARIABLE_PATTERN.findall(
            value
        )

    ]


def resolve_string(
    value,
    state: StateManager
):

    if not isinstance(
        value,
        str
    ):

        return value

    variables = extract_variables(
        value
    )

    for variable in variables:

        resolved = state.get(
            variable
        )

        if resolved is None:

            continue

        value = value.replace(

            "{{"
            + variable
            + "}}",

            str(resolved)

        )

    return value


def resolve_recursive(
    value,
    state: StateManager
):

    if isinstance(
        value,
        str
    ):

        return resolve_string(
            value,
            state
        )

    if isinstance(
        value,
        dict
    ):

        return {

            key:
                resolve_recursive(
                    item,
                    state
                )

            for key, item
            in value.items()

        }

    if isinstance(
        value,
        list
    ):

        return [

            resolve_recursive(
                item,
                state
            )

            for item
            in value

        ]

    return value


def unresolved_variables(
    value,
    state
):

    variables = []

    if isinstance(
        value,
        str
    ):

        for variable in extract_variables(
            value
        ):

            if not state.has(
                variable
            ):

                variables.append(
                    variable
                )

    elif isinstance(
        value,
        dict
    ):

        for item in value.values():

            variables.extend(

                unresolved_variables(
                    item,
                    state
                )

            )

    elif isinstance(
        value,
        list
    ):

        for item in value:

            variables.extend(

                unresolved_variables(
                    item,
                    state
                )

            )

    return list(
        dict.fromkeys(
            variables
        )
    )


def resolve_request(
    request,
    state
):

    return {

        "method":
            resolve_recursive(
                request.method,
                state
            ),

        "url":
            resolve_recursive(
                request.url,
                state
            ),

        "headers":
            resolve_recursive(
                request.headers,
                state
            ),

        "params":
            resolve_recursive(
                request.params,
                state
            ),

        "body":
            resolve_recursive(
                request.body,
                state
            )

    }