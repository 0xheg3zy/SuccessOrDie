class StateManager:

    def __init__(
        self,
        static_variables=None
    ):

        self.static = (
            static_variables.copy()
            if static_variables
            else {}
        )

        self.dynamic = {}

    def set_static(
        self,
        key,
        value
    ):

        self.static[key] = value

    def set_dynamic(
        self,
        key,
        value
    ):

        self.dynamic[key] = value

    def get(
        self,
        key,
        default=None
    ):

        # Dynamic variables have priority

        if key in self.dynamic:

            return self.dynamic[key]

        if key in self.static:

            return self.static[key]

        return default

    def has(
        self,
        key
    ):

        return (

            key in self.dynamic

            or

            key in self.static

        )

    def all(
        self
    ):

        result = {}

        result.update(
            self.static
        )

        result.update(
            self.dynamic
        )

        return result

    def static_values(
        self
    ):

        return self.static.copy()

    def dynamic_values(
        self
    ):

        return self.dynamic.copy()

    def __repr__(
        self
    ):

        return repr(
            self.all()
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

                index = int(
                    key
                )

                current = current[
                    index
                ]

            except (
                ValueError,
                IndexError
            ):

                return None

        else:

            return None

    return current