from typing import Optional, Dict, Any, List, IO
import os
import json
from dataclasses import dataclass


from compman import config


@dataclass
class StoredCompetition:
    id: str
    title: str
    soaringspot_url: Optional[str] = None
    airspace: Optional[str] = None
    waypoints: Optional[str] = None

    @classmethod
    def fromdict(cls, id: str, data: Dict[str, Any]) -> "StoredCompetition":
        return cls(
            id=id,
            title=data["title"],
            soaringspot_url=data.get("soaringspot_url"),
            airspace=data.get("airspace"),
            waypoints=data.get("waypoints"),
        )

    def asdict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "soaringspot_url": self.soaringspot_url,
            "airspace": self.airspace,
            "waypoints": self.waypoints,
            "version": 1,
        }


@dataclass
class StoredFile:
    name: str
    size: Optional[int]

    def format_size(self):
        if self.size is None:
            return "?"
        suffix = "B"
        for unit in ["", "Ki", "Mi", "Gi"]:
            if abs(self.size) < 1024.0:
                return "%3.1f%s%s" % (self.size, unit, suffix)
            self.size /= 1024.0
        return "%.1f%s%s" % (self.size, "Yi", suffix)


def init() -> None:
    datadir = config.get().datadir
    os.makedirs(datadir, mode=0o755, exist_ok=True)


def save_competition(comp: StoredCompetition) -> None:
    compdir = _get_compdir(comp.id)

    if not os.path.exists(compdir):
        os.mkdir(compdir, 0o755)

    with open(_get_compconfigname(comp.id), "wt") as f:
        compdict = comp.asdict()
        json.dump(compdict, f, indent=2)
        f.write("\n")


def load_competiton(cid: str) -> Optional[StoredCompetition]:
    if not exists(cid):
        return None

    with open(_get_compconfigname(cid), "rt") as f:
        compdict = json.load(f)
        comp = StoredCompetition.fromdict(cid, compdict)

    return comp


def store_file(cid: str, filename: str, contents: IO[bytes]) -> StoredFile:
    cdir = _get_compdir(cid)
    fullname = os.path.join(cdir, filename)
    with open(fullname, "wb") as f:
        f.write(contents.read())
    return StoredFile(name=filename, size=os.path.getsize(fullname))


def get_airspace_files(cid: str) -> List[StoredFile]:
    return _get_files(cid, ".txt")


def get_waypoint_files(cid: str) -> List[StoredFile]:
    return _get_files(cid, ".cup")


def _get_files(cid: str, ext: str) -> List[StoredFile]:
    cdir = _get_compdir(cid)

    files = []
    for entry in os.scandir(cdir):
        if entry.is_dir():
            continue
        if not entry.name.endswith(ext):
            continue
        stat = entry.stat()
        files.append(StoredFile(name=entry.name, size=stat.st_size))
    return files


def exists(cid: str) -> bool:
    compdir = _get_compdir(cid)
    return os.path.exists(compdir)


def get_all() -> List[StoredCompetition]:
    datadir = config.get().datadir
    competitions = []
    for cid in os.listdir(datadir):
        conffname = _get_compconfigname(cid)
        if not os.path.exists(conffname):
            continue
        comp = load_competiton(cid)
        competitions.append(comp)

    return competitions


def _get_compdir(cid: str) -> str:
    datadir = config.get().datadir
    return os.path.join(datadir, cid)


def _get_compconfigname(cid: str) -> str:
    compdir = _get_compdir(cid)
    return os.path.join(compdir, "competition.json")
