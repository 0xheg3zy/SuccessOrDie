class StateManager:

    def __init__(
        self,
        initial=None
    ):

        self._state = (
            initial.copy()
            if initial
            else {}
        )

    def set(
        self,
        key,
        value
    ):

        self._state[
            key
        ] = value

    def get(
        self,
        key,
        default=None
    ):

        return self._state.get(
            key,
            default
        )

    def all(self):

        return self._state.copy()

    def has(
        self,
        key
    ):

        return key in self._state

    def __repr__(
        self
    ):

        return repr(
            self._state
        )


def extract_json_value(
    data,
    path
):

    current = data

    for key in path.split("."):

        if isinstance(
            current,
            dict
        ):

            if key not in current:

                return None

            current = current[
                key
            ]

        elif isinstance(
            current,
            list
        ):

            try:

                current = current[
                    int(key)
                ]

            except (
                ValueError,
                IndexError
            ):

                return None

        else:

            return None

    return current