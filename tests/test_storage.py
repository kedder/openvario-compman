import os
import io


from compman import storage


def test_get_settings_new(storage_dir) -> None:
    settings = storage.get_settings()
    assert settings is not None
    assert settings.current_competition_id is None


def test_get_settings_bad_file(storage_dir) -> None:
    # GIVEN
    settings_fname = storage._get_settings_fname()
    with open(settings_fname, "w") as f:
        f.write(";garbage;")

    # WHEN
    settings = storage.get_settings()

    # THEN
    assert settings is not None
    assert settings.current_competition_id is None


def test_save_settings_new(storage_dir) -> None:
    # WHEN
    storage.save_settings()

    # THEN
    settings_fname = storage._get_settings_fname()
    assert os.path.exists(settings_fname)


def test_save_settings_modified(storage_dir) -> None:
    settings = storage.get_settings()
    settings.current_competition_id = "hello"

    # WHEN
    storage.save_settings()

    # THEN
    settings = storage.load_settings()
    assert settings.current_competition_id == "hello"


def test_list_competitions_empty(storage_dir) -> None:
    # WHEN
    comps = storage.list_competitions()

    # THEN
    assert comps == []


def test_save_competition(storage_dir) -> None:
    # GIVEN
    comp = storage.StoredCompetition(
        id="first",
        title="First Competition",
        soaringspot_url="http://localhost",
        airspace="airspace.txt",
        waypoints="waypoints.txt",
    )

    # WHEN
    storage.save_competition(comp)

    # THEN
    comps = storage.list_competitions()
    assert [c.id for c in comps] == ["first"]


def test_load_competition_missing(storage_dir) -> None:
    # WHEN
    comp = storage.load_competition("missing")

    # THEN
    assert comp is None


def test_load_competition_existing(storage_dir) -> None:
    # GIVEN
    comp = storage.StoredCompetition(
        id="first",
        title="First Competition",
        soaringspot_url="http://localhost",
        airspace="airspace.txt",
        waypoints=None,
    )
    storage.save_competition(comp)

    # WHEN
    loaded = storage.load_competition("first")
    assert loaded is not None

    # THEN
    assert loaded.id == "first"
    assert loaded.title == "First Competition"
    assert loaded.soaringspot_url == "http://localhost"
    assert loaded.airspace == "airspace.txt"
    assert loaded.waypoints == None


def test_store_file(storage_dir) -> None:
    # GIVEN
    comp = storage.StoredCompetition(id="first", title="First Competition")
    storage.save_competition(comp)

    # WHEN
    storage.store_file("first", "airspace.txt", io.BytesIO(b"test"))

    # THEN
    files = storage.get_airspace_files("first")
    assert [f.name for f in files] == ["airspace.txt"]
    files = storage.get_waypoint_files("first")
    assert files == []


def test_get_waypoint_files(storage_dir) -> None:
    # GIVEN
    comp = storage.StoredCompetition(id="first", title="First Competition")
    storage.save_competition(comp)

    # WHEN
    storage.store_file("first", "waypoint.cup", io.BytesIO(b"test"))

    files = storage.get_waypoint_files("first")
    assert [f.name for f in files] == ["waypoint.cup"]
    files = storage.get_airspace_files("first")
    assert files == []


def test_storedfile_format_size() -> None:
    assert storage.StoredFile("", size=1024).format_size() == "1.0KiB"
    assert storage.StoredFile("", size=1).format_size() == "1.0B"
    assert storage.StoredFile("", size=100000).format_size() == "97.7KiB"
    assert storage.StoredFile("", size=10000000).format_size() == "9.5MiB"
    assert storage.StoredFile("", size=None).format_size() == "?"
    assert storage.StoredFile("", size=2 ** 32).format_size() == "4.0GiB"
    assert storage.StoredFile("", size=2 ** 48).format_size() == "256.0TiB"


def test_get_full_file_path(storage_dir) -> None:
    path = storage.get_full_file_path("test", "airspace.txt")
    assert path == os.path.join(storage_dir, "test", "airspace.txt")
