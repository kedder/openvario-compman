from typing import Optional, List
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
        self._set_option("AirspaceFile", f"%LOCAL_PATH%\\{fname}")

    def set_waypoint(self, filename: str) -> None:
        fname = "compman-waypoints.cup"
        copyfile(filename, os.path.join(self.xcsoardir, fname))
        self._set_option("WPFile", f"%LOCAL_PATH%\\{fname}")

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


def list_xcsoar_profiles() -> List[str]:
    assert XCSOAR_DIR is not None

    profiles = []
    for fname in os.listdir(XCSOAR_DIR):
        if fname.endswith(".prf"):
            profiles.append(fname)

    return profiles


def get_xcsoar_profile_filename(profile_fname: str) -> str:
    assert XCSOAR_DIR is not None
    return os.path.join(XCSOAR_DIR, profile_fname)


def get_xcsoar_profile(profile_fname: str) -> XCSoarProfile:
    profile_fullname = get_xcsoar_profile_filename(profile_fname)
    return XCSoarProfile(profile_fullname)
