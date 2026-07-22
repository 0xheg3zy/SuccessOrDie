import re


VARIABLE_PATTERN = re.compile(
    r"\{\{\s*([^}]+?)\s*\}\}"
)


def resolve_string(
    value,
    state
):

    if not isinstance(
        value,
        str
    ):

        return value

    def replace(match):

        key = match.group(
            1
        ).strip()

        result = state.get(
            key
        )

        if result is None:

            return match.group(
                0
            )

        return str(result)

    return VARIABLE_PATTERN.sub(
        replace,
        value
    )


def resolve_recursive(
    value,
    state
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

            key: resolve_recursive(
                val,
                state
            )

            for key, val
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

            for item in value

        ]

    return value