from typing import List, IO
import re
import io
from enum import Enum
from dataclasses import dataclass
from aiohttp import ClientSession

from lxml import etree


SOARINGSPOT_URL = "https://www.soaringspot.com"


class DownloadableFileType(Enum):
    UNKNOWN = "unknown"
    AIRSPACE = "airspace"
    WAYPOINT = "waypoint"


@dataclass
class SoaringSpotDownloadableFile:
    filename: str
    href: str
    kind: DownloadableFileType = DownloadableFileType.UNKNOWN


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
            SoaringSpotContest(
                id=cid, href=f"{SOARINGSPOT_URL}{href}", title=title, description=descr
            )
        )

    return contests


async def fetch_downloads(comp_url: str) -> List[SoaringSpotDownloadableFile]:
    dl_url = f"{_sanitize_url(comp_url)}/downloads"
    async with ClientSession() as session:
        async with session.get(dl_url) as response:
            html = await response.text()

    parser = etree.HTMLParser()
    root = etree.parse(io.StringIO(html), parser)

    dls = []
    for anode in root.xpath("//ul[@class='contest-downloads']/li/a"):
        filename = " ".join(anode.itertext()).strip()
        url = anode.attrib["href"]
        if not url.startswith("http"):
            url = f"{SOARINGSPOT_URL}{url}"
        dl = SoaringSpotDownloadableFile(filename=filename, href=url)
        if filename.endswith(".txt"):
            dl.kind = DownloadableFileType.AIRSPACE
        elif filename.endswith(".cup"):
            dl.kind = DownloadableFileType.WAYPOINT

        if dl.kind != DownloadableFileType.UNKNOWN:
            dls.append(dl)

    return dls


async def fetch_file(file_url: str) -> IO[bytes]:
    async with ClientSession() as session:
        async with session.get(file_url) as response:
            content = await response.read()

    return io.BytesIO(content)


def _extract_text(els) -> str:
    texts: List[str] = []
    for el in els:
        texts.extend(el.itertext())

    joined = " ".join(texts)
    return re.sub(r"[ \n]+", " ", joined).strip()


def _sanitize_url(url: str) -> str:
    return url.rstrip("/")
