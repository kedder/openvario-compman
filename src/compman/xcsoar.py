import os


class XCSoarProfile:
    def __init__(self, filename):
        self.filename = filename

        with open(filename, "rt") as f:
            self.lines = f.readlines()

    def save(self):
        with open(self.filename, "wt") as f:
            f.write("".join(self.lines))

    def set_airspace(self, filename: str) -> None:
        self._set_option("AirspaceFile", filename)

    def set_waypoint(self, filename: str) -> None:
        self._set_option("WPFile", filename)

    def _set_option(self, key: str, value: str) -> None:
        modified_line = f'{key}="{value}"\n'
        for n, line in enumerate(self.lines):
            k, v = line.split("=", maxsplit=1)
            if k == key:
                self.lines[n] = modified_line
                break
        else:
            self.lines.append(modified_line)


def find_xcsoar_dir() -> str:
    home = os.path.expanduser("~")
    xcsoardir = os.path.join(home, ".xcsoar")
    if not os.path.exists(xcsoardir):
        raise FileNotFoundError(xcsoardir)
    return xcsoardir


def find_xcsoar_profile_filename() -> str:
    xcsdir = find_xcsoar_dir()
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
