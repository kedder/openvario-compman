from typing import Optional, Dict, Any, List, IO
import logging
import os
import json
from dataclasses import dataclass, field

DEFAULT_DATADIR = "~/.compman"

_DATADIR: Optional[str]
_SETTINGS: Optional["Settings"] = None

log = logging.getLogger("compman")


@dataclass
class Settings:
    current_competition_id: Optional[str] = None

    @classmethod
    def fromdict(cls, data: Dict[str, Any]) -> "Settings":
        return cls(current_competition_id=data.get("current_competition_id"))

    def asdict(self) -> Dict[str, Any]:
        return {"current_competition_id": self.current_competition_id}


@dataclass
class StoredCompetition:
    id: str
    title: str
    soaringspot_url: Optional[str] = None
    airspace: Optional[str] = None
    waypoints: Optional[str] = None
    profiles: List[str] = field(default_factory=list)

    @classmethod
    def fromdict(cls, id: str, data: Dict[str, Any]) -> "StoredCompetition":
        return cls(
            id=id,
            title=data["title"],
            soaringspot_url=data.get("soaringspot_url"),
            airspace=data.get("airspace"),
            waypoints=data.get("waypoints"),
            profiles=data.get("profiles") or [],
        )

    def asdict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "soaringspot_url": self.soaringspot_url,
            "airspace": self.airspace,
            "waypoints": self.waypoints,
            "profiles": self.profiles,
            "version": 1,
        }

    def add_profile(self, profile) -> None:
        if profile not in self.profiles:
            self.profiles.append(profile)

    def remove_profile(self, profile: str) -> None:
        if profile in self.profiles:
            self.profiles.remove(profile)


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
        return "%.1f%s%s" % (self.size, "Ti", suffix)


def init(datadir: str) -> None:
    global _DATADIR, _SETTINGS
    _DATADIR = datadir
    os.makedirs(datadir, mode=0o755, exist_ok=True)
    _SETTINGS = None


def deinit() -> None:
    global _DATADIR, _SETTINGS
    _DATADIR = None
    _SETTINGS = None


def get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = load_settings()

    return _SETTINGS


def load_settings() -> Settings:
    fname = _get_settings_fname()
    if os.path.exists(fname):
        with open(fname) as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                log.error(f"Cannot load settings file: {fname}")
                data = {}
    else:
        data = {}
    return Settings.fromdict(data)


def save_settings() -> None:
    settings = get_settings()
    fname = _get_settings_fname()
    with open(fname, "w") as f:
        json.dump(settings.asdict(), f, indent=2)


def save_competition(comp: StoredCompetition, set_current: bool = False) -> None:
    compdir = _get_compdir(comp.id)

    if not os.path.exists(compdir):
        os.mkdir(compdir, 0o755)

    with open(_get_compconfigname(comp.id), "wt") as f:
        compdict = comp.asdict()
        json.dump(compdict, f, indent=2)
        f.write("\n")

    if set_current:
        get_settings().current_competition_id = comp.id
        save_settings()


def load_competition(cid: str) -> Optional[StoredCompetition]:
    if not exists(cid):
        return None

    with open(_get_compconfigname(cid), "rt") as f:
        compdict = json.load(f)
        comp = StoredCompetition.fromdict(cid, compdict)

    return comp


def list_competitions() -> List[StoredCompetition]:
    competitions = []
    for cid in os.listdir(_DATADIR):
        comp = load_competition(cid)
        if comp is None:
            continue
        competitions.append(comp)

    return sorted(competitions, key=lambda c: c.title)


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


def get_full_file_path(cid: str, fname: str) -> str:
    return os.path.abspath(os.path.join(_get_compdir(cid), fname.strip()))


def exists(cid: str) -> bool:
    configfname = _get_compconfigname(cid)
    return os.path.exists(configfname)


def _get_compdir(cid: str) -> str:
    assert _DATADIR
    return os.path.join(_DATADIR, cid)


def _get_compconfigname(cid: str) -> str:
    compdir = _get_compdir(cid)
    return os.path.join(compdir, "competition.json")


def _get_settings_fname() -> str:
    assert _DATADIR
    return os.path.join(_DATADIR, "settings.json")
