from typing import List, Optional
import io
from dataclasses import dataclass
import re

from aiohttp import ClientSession
from lxml import etree


SOARSCORE_URL = "https://soarscore.com/"

SOARSCORE_TASK_DESC_RE = r"(.*) Day([0-9]+) Task([0-9]+) (.*) \.tsk generated: (.*)"


@dataclass
class SoarScoreTaskInfo:
    comp_class: str
    title: str
    day_no: int
    task_no: int
    timestamp: str
    task_url: str


async def fetch_latest_tasks(comp_id: str) -> List[SoarScoreTaskInfo]:
    comp_url = f"{SOARSCORE_URL}/competitions/{comp_id}/"
    async with ClientSession() as session:
        async with session.get(comp_url) as response:
            html = await response.text()

    parser = etree.HTMLParser()
    root = etree.parse(io.StringIO(html), parser)

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
