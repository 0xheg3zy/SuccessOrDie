import json

from .models import APIRequest


def load_collection(path: str):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def extract_variables(collection):

    variables = {}

    for variable in collection.get(
        "variable",
        []
    ):

        key = variable.get("key")

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

            result[
                item.get("key")
            ] = item.get(
                "value",
                ""
            )

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

            # Folder
            if "item" in item:

                walk_items(
                    item["item"]
                )

                continue

            # Request
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
                ),

                url=extract_url(
                    request
                ),

                headers=extract_request_headers(
                    request
                ),

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