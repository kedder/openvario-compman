from dataclasses import dataclass
import configparser


@dataclass
class Config:
    datadir: str


_config: Config = None


def load() -> Config:
    configfile = "compman.ini"
    config = configparser.ConfigParser()
    config.read(configfile)

    return Config(datadir=config["compman"]["datadir"])


def set(config: Config) -> None:
    global _config
    _config = config


def get() -> Config:
    global _config
    if _config is None:
        raise RuntimeError("Not configured")
    return _config
