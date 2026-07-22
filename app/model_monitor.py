import sys
import time

from .config import (
    DEFAULT_MODEL_STATUS_TIMEOUT,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_MODEL
)


def format_bytes(
    value
):

    if value is None:

        return "unknown"

    value = float(
        value
    )

    units = [

        "B",
        "KB",
        "MB",
        "GB",
        "TB"

    ]

    for unit in units:

        if value < 1024:

            return (

                f"{value:.2f} "
                f"{unit}"

            )

        value /= 1024

    return (

        f"{value:.2f} PB"

    )


def progress_bar(
    percentage,
    width=30
):

    percentage = max(

        0.0,

        min(
            100.0,
            percentage
        )

    )

    filled = int(

        width
        *
        percentage
        /
        100

    )

    return (

        "["
        + "#"
        * filled
        + "-"
        * (
            width
            -
            filled
        )
        + "]"

    )


def get_running_model(
    client,
    base_url,
    model,
    timeout
):

    try:

        response = client.get(

            base_url.rstrip("/")
            + "/api/ps",

            timeout=
                timeout

        )

        response.raise_for_status()

        data = response.json()

    except Exception as error:

        print(

            f"\n[!] Could not query "
            f"Ollama model status: "
            f"{error}"

        )

        return None

    for running_model in data.get(
        "models",
        []
    ):

        name = running_model.get(
            "name",
            ""
        )

        if (

            name == model

            or

            name.startswith(
                model + ":"
            )

        ):

            return running_model

    return None


def get_model_info(
    client,
    base_url,
    model,
    timeout
):

    try:

        response = client.post(

            base_url.rstrip("/")
            + "/api/show",

            json={

                "name":
                    model

            },

            timeout=
                timeout

        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return {}


def print_model_status(
    client,
    base_url=DEFAULT_OLLAMA_BASE_URL,
    model=DEFAULT_OLLAMA_MODEL,
    timeout=DEFAULT_MODEL_STATUS_TIMEOUT
):

    running = get_running_model(

        client,

        base_url,

        model,

        timeout

    )

    if not running:

        print(

            "\n[MODEL] "
            f"{model} is not currently "
            "loaded in Ollama memory."

        )

        return None

    size = running.get(
        "size"
    )

    size_vram = running.get(
        "size_vram"
    )

    if size_vram is not None:

        loaded = size_vram

        location = "VRAM"

    else:

        loaded = size

        location = "RAM"

    if (

        size
        and
        loaded is not None

    ):

        percentage = (

            loaded
            /
            size
            *
            100

        )

    else:

        percentage = 100.0

    bar = progress_bar(

        percentage

    )

    print(

        "\n[MODEL] "
        f"{model}"

    )

    print(

        f"[MODEL] {location}: "
        f"{format_bytes(loaded)}"

    )

    print(

        f"[MODEL] Model size: "
        f"{format_bytes(size)}"

    )

    print(

        f"[MODEL] Residency: "
        f"{bar} "
        f"{percentage:.2f}%"

    )

    return {

        "name":
            running.get(
                "name"
            ),

        "size":
            size,

        "size_vram":
            size_vram,

        "loaded_bytes":
            loaded,

        "location":
            location,

        "percentage":
            percentage

    }


def wait_for_model_loaded(
    client,
    base_url,
    model,
    timeout=DEFAULT_MODEL_STATUS_TIMEOUT,
    interval=1
):

    print(

        f"\n[MODEL] Waiting for "
        f"{model} to load..."

    )

    last_percentage = -1

    while True:

        running = get_running_model(

            client,

            base_url,

            model,

            timeout

        )

        if running:

            size = running.get(
                "size"
            )

            size_vram = running.get(
                "size_vram"
            )

            if size_vram is not None:

                loaded = size_vram

                location = "VRAM"

            else:

                loaded = size

                location = "RAM"

            if (

                size
                and
                loaded is not None

            ):

                percentage = (

                    loaded
                    /
                    size
                    *
                    100

                )

            else:

                percentage = 100

            if percentage != last_percentage:

                bar = progress_bar(

                    percentage

                )

                sys.stdout.write(

                    "\r[MODEL] "
                    f"{location} "
                    f"{bar} "
                    f"{percentage:.2f}%"

                )

                sys.stdout.flush()

                last_percentage = percentage

            if percentage >= 99.0:

                print()

                return running

        time.sleep(
            interval
        )