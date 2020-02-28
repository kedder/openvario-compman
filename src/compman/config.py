from typing import Optional

from dataclasses import dataclass
import configparser


@dataclass
class Config:
    datadir: str
    current_competition_id: Optional[str]


_config: Config = None


def load() -> Config:
    configfile = _get_config_fname()
    config = configparser.ConfigParser()
    config.read(configfile)
    comp_sec = config["compman"]

    return Config(
        datadir=comp_sec["datadir"],
        current_competition_id=comp_sec.get("current-competition-id"),
    )


def save():
    config = get()
    cp = configparser.ConfigParser()
    cp["compman"] = {
        "datadir": config.datadir,
        "current-competition-id": config.current_competition_id,
    }
    configfile = _get_config_fname()
    with open(configfile, "w") as f:
        cp.write(f)


def set(config: Config) -> None:
    global _config
    _config = config


def get() -> Config:
    global _config
    if _config is None:
        raise RuntimeError("Not configured")
    return _config


def _get_config_fname():
    return "compman.ini"
