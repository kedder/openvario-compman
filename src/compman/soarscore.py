from typing import List, Optional
import io
from dataclasses import dataclass
import asyncio
import re

import requests
from lxml import etree


SOARSCORE_URL = "https://soarscore.com"

SOARSCORE_TASK_DESC_RE = r"(.*) Day([0-9]+) Task([0-9]+) (.*) \.tsk generated: (.*)"


@dataclass
class SoarScoreTaskInfo:
    comp_class: str
    title: str
    day_no: int
    task_no: int
    timestamp: str
    task_url: str


def _fetch_url(url) -> bytes:
    resp = requests.get(url)
    return resp.content


async def fetch_url(url) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch_url, url)


async def fetch_latest_tasks(comp_id: str) -> List[SoarScoreTaskInfo]:
    # Soarscore serves on HTTP/2 and aiohttp cannot handle that. Run synchronous
    # requests
    # instead.
    comp_url = f"{SOARSCORE_URL}/competitions/{comp_id}/"
    html = await fetch_url(comp_url)

    parser = etree.HTMLParser()
    root = etree.parse(io.BytesIO(html), parser)

    task_links = root.xpath('//*[@id="Downloads"]//a[@download]')
    tasks = []
    for link in task_links:
        href = link.attrib["href"]
        raw_descr = " ".join(list(link.itertext())).strip()
        task_info = parse_soarscore_description(href, raw_descr)
        if task_info is not None:
            tasks.append(task_info)

    return tasks


def parse_soarscore_description(
    href: str, raw_descr: str
) -> Optional[SoarScoreTaskInfo]:
    m = re.match(SOARSCORE_TASK_DESC_RE, raw_descr)
    if m is None:
        return None

    cls = m.group(1)
    day = m.group(2)
    task = m.group(3)
    title = m.group(4)
    timestamp = m.group(5)

    return SoarScoreTaskInfo(
        comp_class=cls,
        title=title,
        day_no=int(day),
        task_no=int(task),
        timestamp=timestamp,
        task_url=href,
    )
