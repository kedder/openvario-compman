from typing import List
import re
import io
from dataclasses import dataclass
from aiohttp import ClientSession
from lxml import etree


SOARINGSPOT_URL = "https://www.soaringspot.com/"


@dataclass
class SoaringSpotContest:
    id: str
    href: str
    title: str
    description: str


async def fetch_competitions() -> List[SoaringSpotContest]:
    async with ClientSession() as session:
        async with session.get(SOARINGSPOT_URL) as response:
            html = await response.text()

    # Parse html
    parser = etree.HTMLParser()
    root = etree.parse(io.StringIO(html), parser)
    contests = []
    for contestelem in root.xpath("//*[@class='contest']"):
        linkel = contestelem.xpath("h3//a")[0]
        title = linkel.text
        href = linkel.attrib["href"]
        descr = _extract_text(contestelem.xpath("*[@class='info']"))
        cid = href.strip(" /").split("/")[-1]

        contests.append(
            SoaringSpotContest(id=cid, href=href, title=title, description=descr)
        )

    return contests


def _extract_text(els) -> str:
    texts = []
    for el in els:
        texts.extend(el.itertext())

    joined = " ".join(texts)
    return re.sub(r"[ \n]+", " ", joined).strip()
