from typing import Optional

import requests


class ProxySession:

    def __init__(
        self,
        proxy: Optional[str] = None,
        verify: bool = True
    ):

        self.proxy = proxy

        self.verify = verify

        self.session = requests.Session()

        if proxy:

            self.session.proxies.update({

                "http":
                    proxy,

                "https":
                    proxy

            })

        self.session.verify = verify

    def request(
        self,
        method,
        url,
        **kwargs
    ):

        kwargs.setdefault(
            "verify",
            self.verify
        )

        if self.proxy:

            kwargs.setdefault(

                "proxies",

                {

                    "http":
                        self.proxy,

                    "https":
                        self.proxy

                }

            )

        return self.session.request(

            method,

            url,

            **kwargs

        )

    def get(
        self,
        url,
        **kwargs
    ):

        return self.request(

            "GET",

            url,

            **kwargs

        )

    def post(
        self,
        url,
        **kwargs
    ):

        return self.request(

            "POST",

            url,

            **kwargs

        )

    def close(
        self
    ):

        self.session.close()