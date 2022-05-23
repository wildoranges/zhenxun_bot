from http.client import USE_PROXY
from utils.http_utils import AsyncHttpx
from configs.config import Config
from configs.path_config import TEMP_PATH
from utils.message_builder import image
from typing import Union, List
import random

API_URL_SAUCENAO = "https://saucenao.com/search.php"
API_URL_ASCII2D = "https://ascii2d.net/search/url/"
API_URL_IQDB = "https://iqdb.org/"


async def get_saucenao_image(url: str) -> Union[str, List[str]]:
    api_key = Config.get_config("search_image", "API_KEY")
    if not api_key:
        return "Saucenao 缺失API_KEY！"

    params = {
        "output_type": 2,
        "api_key": api_key,
        "testmode": 1,
        "numres": 6,
        "db": 999,
        "url": url,
    }
    proxies = {}
    is_proxy = False
    http_proxy = Config.get_config("search_image", "HTTP_PROXY")
    if http_proxy :
        proxies["http://"] = http_proxy
        is_proxy = True
    https_proxy = Config.get_config("search_image", "HTTPS_PROXY")
    if https_proxy :
        proxies["https://"] = https_proxy
        is_proxy = True
    if not is_proxy :
        proxies = None
    print(proxies)
    data = (await AsyncHttpx.post(API_URL_SAUCENAO, params=params, use_proxy=is_proxy, proxy=proxies)).json()
    if data["header"]["status"] != 0:
        return f"Saucenao识图失败..status：{data['header']['status']}"
    data = data["results"]
    data = (
        data
        if len(data) < Config.get_config("search_image", "MAX_FIND_IMAGE_COUNT")
        else data[: Config.get_config("search_image", "MAX_FIND_IMAGE_COUNT")]
    )
    msg_list = []
    index = random.randint(0, 10000)
    if await AsyncHttpx.download_file(
            url, TEMP_PATH / f"saucenao_search_{index}.jpg"
    ):
        msg_list.append(image(TEMP_PATH / f"saucenao_search_{index}.jpg"))
    for info in data:
        similarity = info["header"]["similarity"]
        tmp = f"相似度：{similarity}%\n"
        for x in info["data"].keys():
            if x != "ext_urls":
                tmp += f"{x}：{info['data'][x]}\n"
        if "source" not in info["data"].keys():
            tmp += f'source：{info["data"]["ext_urls"][0]}\n'
        msg_list.append(tmp[:-1])
    return msg_list
