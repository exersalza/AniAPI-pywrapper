#!/bin/python3
#  MIT License
#
#  Copyright (c) 2022 by exersalza
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import http.client
import json
import pprint
import time

from urllib.parse import urlencode
from typing import Union, List

from _types.anime import Anime
from _types.context import Context

from config import API_TOKEN
from convertor import AnimeObj, ContextObj, DataObj
from utils import InvalidParamsException, ANIME_REQ
from constants import API_VERSION, DEFAULT_HEADER


class AniApi(http.client.HTTPSConnection):
    def __init__(self, token: str = '', port: int = 443, timeout: int = None):
        """ This is the Base Class for the AniApi wrapper.

        :param token: (str) --
            You only need a Token when your Application is **not** in the read-only scope.

        :param port: (int) --
            When you want to set the port to another to avoid conflicts with other services.

        :param timeout: (float) --
            The optional timeout parameter is given, blocking operations (like connection attempts)
            will `timeout` after that many seconds.

        """
        super().__init__(host='api.aniapi.com', port=port, timeout=timeout)

        # Define default headers with token
        self.headers = DEFAULT_HEADER(token)

    # Here comes all the Anime related methods.
    def get_anime(self, _id=None, **kwargs) -> Context:
        """
        Get an Anime list with 100 Animes or when you provide an ID it will give you the Anime with the related ID.

        It will raise an **InvalidFlagsException** when you give any Kwargs that are not supported.

        Supported Parameters can be found at: https://aniapi.com/docs/resources/anime/#parameters-1 page.

        :param _id: ID of the Anime [OPTIONAL]
        :param kwargs: Used for specific anime search.
        :return: Dictionary with the response
        """
        invalid = set(kwargs) - set(ANIME_REQ)

        if invalid:
            raise InvalidParamsException(f'Invalid parameters: {invalid}')

        self.request('GET', f'/{API_VERSION}/anime/{_id if _id else ""}?{urlencode(kwargs)}', headers=self.headers)

        res = self.getresponse()
        pprint.pprint(dict(res.headers))  # debug
        res_read = res.read()
        data = json.loads(res_read.decode('utf-8'))

        if _id is not None:
            data['data'] = AnimeObj(**data['data'])
            return ContextObj(**data)

        data['data']['documents'] = [AnimeObj(**anime) for anime in data['data']['documents']]
        # print(data)
        data['data'] = DataObj(**data['data'])
        return ContextObj(**data)

    def get_random_anime(self, count: int = 1, nsfw: bool = False) -> Anime:
        """
        Get a random Anime object.

        i.e. `client.get_random_anime(1, True)` - This will return an object of 1 random Anime with NSFW content.

        :param count: (int) --
            Give an amount of Anime to get
        :param nsfw: (bool) --
            Is it safe for work? right?
        :return: object.Anime --
            Dictionary with the response
        """

        self.request('GET', f'/{API_VERSION}/random/anime/{count}/{nsfw}', headers=self.headers)

        res = self.getresponse()
        data = json.loads(res.read().decode('utf-8'))
        return AnimeObj(**data.get('data')[0])

    # Here comes all the Episode related methods.
    def get_episode(self, _id=None) -> dict:
        """
        Get an Episode with the related ID.

        :param _id: ID of the Episode
        :return: Dictionary with the response
        """

        self.request('GET', f'/{API_VERSION}/episode/{_id if _id else ""}', headers=self.headers)

        res = self.getresponse()
        return json.loads(res.read().decode('utf-8'))


if __name__ == '__main__':
    start = time.time()
    client = AniApi(token=API_TOKEN)
    data: Context = client.get_anime()

    # for i in data:
    #     print(i)
    # print(data)
    end = time.time()

    print(f'Time: {(end - start):.2f}s')
    # print(client.get_anime(_id=1))
