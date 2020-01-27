from typing import Optional, Dict, Any, List
import os
import json
from dataclasses import dataclass


from compman import config


@dataclass
class StoredCompetition:
    id: str
    title: str
    soaringspot_url: Optional[str] = None

    @classmethod
    def fromdict(cls, id: str, data: Dict[str, Any]) -> "StoredCompetition":
        return cls(
            id=id, title=data["title"], soaringspot_url=data.get("soaringspot_url")
        )

    def asdict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "soaringspot_url": self.soaringspot_url,
            "version": 1,
        }


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


def load_competiton(cid: str) -> StoredCompetition:
    if not exists(cid):
        raise RuntimeError(f"Competition {cid} does not exist")

    with open(_get_compconfigname(cid), "rt") as f:
        compdict = json.load(f)
        comp = StoredCompetition.fromdict(cid, compdict)

    return comp


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
