from typing import Optional
from shutil import copyfile
import os


XCSOAR_DIR: Optional[str] = None


class XCSoarProfile:
    def __init__(self, filename):
        self.filename = filename
        self.xcsoardir = os.path.dirname(filename)

        with open(filename, "rt") as f:
            self.lines = f.readlines()

    def save(self):
        with open(self.filename, "wt") as f:
            f.write("".join(self.lines))

    def set_airspace(self, filename: str) -> None:
        fname = "compman-airspace.txt"
        copyfile(filename, os.path.join(self.xcsoardir, fname))
        self._set_option("AirspaceFile", fname)

    def set_waypoint(self, filename: str) -> None:
        fname = "compman-waypoints.cup"
        copyfile(filename, os.path.join(self.xcsoardir, fname))
        self._set_option("WPFile", fname)

    def _set_option(self, key: str, value: str) -> None:
        modified_line = f'{key}="{value}"\n'
        for n, line in enumerate(self.lines):
            k, v = line.split("=", maxsplit=1)
            if k == key:
                self.lines[n] = modified_line
                break
        else:
            self.lines.append(modified_line)


def init(xcsoar_dir: str = None) -> None:
    global XCSOAR_DIR
    if xcsoar_dir is None:
        xcsoar_dir = find_xcsoar_dir()
    XCSOAR_DIR = xcsoar_dir


def deinit() -> None:
    global XCSOAR_DIR
    XCSOAR_DIR = None


def find_xcsoar_dir() -> str:
    home = os.path.expanduser("~")
    xcsoardir = os.path.join(home, ".xcsoar")
    if not os.path.exists(xcsoardir):
        raise FileNotFoundError(xcsoardir)
    return xcsoardir


def find_xcsoar_profile_filename() -> str:
    assert XCSOAR_DIR is not None
    xcsdir = XCSOAR_DIR
    defaultprf = os.path.join(xcsdir, "default.prf")
    if os.path.exists(defaultprf):
        return defaultprf

    for f in os.listdir(xcsdir):
        if f.endswith(".prf"):
            return os.path.join(xcsdir, f)

    raise FileNotFoundError(defaultprf)


def get_xcsoar_profile() -> XCSoarProfile:
    prfname = find_xcsoar_profile_filename()
    return XCSoarProfile(prfname)
