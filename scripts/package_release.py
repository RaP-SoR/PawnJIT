#!/usr/bin/env python3
"""Pack one pawn.json resource into a release archive.

The archive name and the paths inside it come from pawn.json. sampctl
matches the name and installs `plugins` plus `files` from those paths.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
import zipfile
from pathlib import Path


def archive_name(pattern: str, version: str) -> str:
    if not pattern.startswith("^") or not pattern.endswith("$"):
        raise SystemExit(f"resource name must be anchored: {pattern}")
    body = pattern[1:-1]
    if not re.search(r"\(\.\+\)|\(\.\*\)", body):
        raise SystemExit(f"resource name has no version group: {pattern}")
    body = re.sub(r"\(\.\+\)|\(\.\*\)", version, body, count=1)
    name = re.sub(r"\\(.)", r"\1", body)
    if not re.fullmatch(pattern, name):
        raise SystemExit(f"{name} does not match {pattern}")
    return name


def find_built(build_dir: Path, filename: str) -> Path:
    matches = [
        path
        for path in build_dir.rglob(filename)
        if path.is_file() and "CMakeFiles" not in path.parts
    ]
    if len(matches) != 1:
        found = ", ".join(str(path) for path in matches) or "none"
        raise SystemExit(f"expected one {filename} in {build_dir}, found: {found}")
    return matches[0]


def resource_paths(resource: dict) -> list[str]:
    paths = list(resource.get("plugins") or [])
    paths.extend(resource.get("files") or [])
    if not paths:
        raise SystemExit(f"resource {resource['name']} lists no files")
    unique = list(dict.fromkeys(paths))
    return unique


def write_archive(destination: Path, members: list[tuple[str, Path]]) -> None:
    if destination.suffix == ".zip":
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for arcname, source in members:
                archive.write(source, arcname.replace("\\", "/"))
        return

    if destination.name.endswith(".tar.gz"):
        with tarfile.open(destination, "w:gz") as archive:
            for arcname, source in members:
                archive.add(source, arcname=arcname.replace("\\", "/"))
        return

    raise SystemExit(f"unsupported archive type: {destination.name}")


def list_archive(archive: Path) -> list[str]:
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zipped:
            return [name.replace("\\", "/") for name in zipped.namelist()]
    with tarfile.open(archive, "r:gz") as tar:
        return [name.replace("\\", "/") for name in tar.getnames() if not name.endswith("/")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True, choices=("linux", "windows"))
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--pawn-json", type=Path, default=Path("pawn.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()

    document = json.loads(args.pawn_json.read_text(encoding="utf-8"))
    matches = [
        resource
        for resource in document["resources"]
        if resource.get("platform") == args.platform
    ]
    if len(matches) != 1:
        raise SystemExit(f"expected one {args.platform} resource in {args.pawn_json}")
    resource = matches[0]

    name = archive_name(resource["name"], args.version)
    paths = resource_paths(resource)
    members = [(path, find_built(args.build_dir, Path(path).name)) for path in paths]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / name
    write_archive(destination, members)

    listed = list_archive(destination)
    if listed != paths:
        raise SystemExit(f"{destination} contains {listed}, expected {paths}")

    print(destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
