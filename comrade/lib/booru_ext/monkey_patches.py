import aiohttp
from booru.utils import fetch
from booru.utils.fetch import Booru
from orjson import dumps


async def init_monkey_patches(session: aiohttp.ClientSession):
    """
    Initialize monkey patches for the booru library.

    Evil hacks used to marginally increase performance.

    Parameters
    ----------
    session : ClientSession
        aiohttp session to use for the booru library.
    """

    # Monkey patch booru library to use orjson instead of json
    def _revised_better_object(parser: dict):
        return dumps(parser, sort_keys=True, indent=4, ensure_ascii=False)

    setattr(fetch, "better_object", _revised_better_object)

    # Monkey patch request function to use bot's aiohttp session
    # instead of creating a new one every time (which is bad)

    async def _revised_request(
        site: str, params_x: dict, ua: dict = Booru.headers, block: str = ""
    ) -> aiohttp.ClientResponse | list | None:
        """Fetch the site

        Parameters
        ----------
        site : str
            The site to request
        params_x : dict
            The parameters to be passed
        ua : dict
            The user agent to be passed
        block : str
            The tags to be blocked

        Returns
        -------
        Union[aiohttp.ClientResponse, list, None]
            The response
        """
        print("using patched request")

        if site == Booru.behoimi:
            ua = Booru.behoimi_bypass

        async with session.get(site, params=params_x, headers=ua) as resp:
            data = await resp.json(content_type=None)
            if not data:
                raise Exception(Booru.error_handling_null)

            if "post" not in data:
                pattern = data

            elif "post" in data:
                pattern = data["post"]

            elif "images" in data:
                pattern = data["images"]

            # Add result count to each post, if it exists
            try:
                print(data.keys())
                result_count = data["@attributes"]["count"]
            except KeyError:
                result_count = None

            try:
                for i in range(len(pattern)):
                    pattern[i]["tags"] = pattern[i]["tags"].split(" ")

                    if result_count:
                        pattern[i]["result_count"] = result_count

                pattern = [
                    i for i in pattern if not any(j in block for j in i["tags"])
                ]

                return pattern

            except Exception as e:  ## danbooru
                if e.args[0] == "tags":
                    for i in range(len(pattern)):
                        pattern[i]["tag_string"] = pattern[i][
                            "tag_string"
                        ].split(" ")

                        pattern = [
                            i
                            for i in pattern
                            if not any(j in block for j in i["tag_string"])
                        ]

                        return pattern

                    else:  ## furry stuff sigh
                        return pattern

    setattr(fetch, "request", _revised_request)
