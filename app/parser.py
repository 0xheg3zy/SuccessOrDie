import json

from .models import APIRequest


def load_json(
    path: str
):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def load_collection(
    path: str
):

    return load_json(
        path
    )


def load_environment(
    path: str | None
):

    if not path:

        return {}

    environment = load_json(
        path
    )

    variables = {}

    for variable in environment.get(
        "values",
        []
    ):

        if not variable.get(
            "enabled",
            True
        ):

            continue

        key = variable.get(
            "key"
        )

        value = variable.get(
            "value"
        )

        if key:

            variables[key] = value

    return variables


def extract_collection_variables(
    collection
):

    variables = {}

    for variable in collection.get(
        "variable",
        []
    ):

        if not variable.get(
            "disabled",
            False
        ):

            key = variable.get(
                "key"
            )

            value = variable.get(
                "value"
            )

            if key:

                variables[key] = value

    return variables


def extract_request_headers(
    request
):

    headers = {}

    for header in request.get(
        "header",
        []
    ):

        if header.get(
            "disabled",
            False
        ):

            continue

        key = header.get(
            "key"
        )

        value = header.get(
            "value",
            ""
        )

        if key:

            headers[key] = value

    return headers


def extract_request_body(
    request
):

    body = request.get(
        "body"
    )

    if not body:

        return None

    mode = body.get(
        "mode"
    )

    if mode == "raw":

        raw = body.get(
            "raw"
        )

        if not raw:

            return None

        try:

            return json.loads(
                raw
            )

        except json.JSONDecodeError:

            return raw

    if mode == "urlencoded":

        result = {}

        for item in body.get(
            "urlencoded",
            []
        ):

            if item.get(
                "disabled",
                False
            ):

                continue

            key = item.get(
                "key"
            )

            value = item.get(
                "value",
                ""
            )

            if key:

                result[key] = value

        return result

    if mode == "formdata":

        result = {}

        for item in body.get(
            "formdata",
            []
        ):

            if item.get(
                "disabled",
                False
            ):

                continue

            if item.get(
                "type",
                "text"
            ) != "text":

                continue

            key = item.get(
                "key"
            )

            value = item.get(
                "value",
                ""
            )

            if key:

                result[key] = value

        return result

    return None


def extract_url(
    request
):

    url = request.get(
        "url"
    )

    if isinstance(
        url,
        str
    ):

        return url

    if isinstance(
        url,
        dict
    ):

        return url.get(
            "raw",
            ""
        )

    return ""


def extract_requests(
    collection
):

    requests = []

    def walk_items(
        items
    ):

        for item in items:

            if "item" in item:

                walk_items(
                    item["item"]
                )

                continue

            if "request" not in item:

                continue

            request = item[
                "request"
            ]

            api_request = APIRequest(

                name=item.get(
                    "name",
                    "Unnamed Request"
                ),

                method=request.get(
                    "method",
                    "GET"
                ).upper(),

                url=extract_url(
                    request
                ),

                headers=extract_request_headers(
                    request
                ),

                params={},

                body=extract_request_body(
                    request
                )
            )

            requests.append(
                api_request
            )

    walk_items(
        collection.get(
            "item",
            []
        )
    )

    return requests