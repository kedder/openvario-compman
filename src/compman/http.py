from typing import IO
import io

from aiohttp import ClientSession


async def fetch_file(file_url: str) -> IO[bytes]:
    async with ClientSession() as session:
        async with session.get(file_url) as response:
            content = await response.read()

    return io.BytesIO(content)
