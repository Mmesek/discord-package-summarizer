import orjson as json
import csv

from zipfile import Path, ZipFile


def load_directory(zip_file: ZipFile, directory: str, files: list[str]) -> dict:
    return {
        _dir.name: {file: load_file(_dir / file) for file in files}
        for _dir in _list_directories(Path(zip_file, at=directory + "/"), ["index.json"])
    }


def _list_directories(path: Path, blacklist: list[str]) -> list[Path]:
    return [i for i in path.iterdir() if i.name not in blacklist]


def load_file(path: Path) -> dict | list[dict]:
    with path.open("r", encoding="utf-8") as file:
        if path.name.endswith("json"):
            return json.loads(file.read())
        elif path.name.endswith("csv"):
            return csv.DictReader(file.readlines())
    raise ValueError("Invalid path. Path should end with either json or csv extenstion")
