"""공식 릴리스 ZIP을 검증한 뒤 두 Cask를 함께 갱신한다. Python 표준 라이브러리와 gh만 사용한다."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = {"font-monatendard": "Desktop", "font-monatendard-nerd-font": "Desktop-Nerd"}


def stable_version(tag):
    if not re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", tag):
        raise ValueError(f"정식 버전 태그만 지원합니다: {tag!r}")
    return tag[1:]


def prepare_updates(root, repository, release, archive_dir):
    """두 ZIP 모두 검증하기 전에는 Cask를 수정하지 않는다."""
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("초안 또는 사전 릴리스는 배포하지 않습니다.")
    version = stable_version(release["tag_name"])
    checksums = (archive_dir / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    updates = {}
    for token, kind in PACKAGES.items():
        path = root / "Casks" / f"{token}.rb"
        content = path.read_text(encoding="utf-8")
        old = re.findall(r'^  version "([^"]+)"$', content, re.MULTILINE)
        if len(old) != 1:
            raise ValueError(f"version 항목 확인 필요: {path}")
        previous = stable_version("v" + old[0])
        if tuple(map(int, version.split("."))) < tuple(map(int, previous.split("."))):
            raise ValueError(f"버전 역행 금지: {old[0]} → {version}")
        filename = f"Monatendard-v{version}-{kind}.zip"
        pattern = re.compile(r"([0-9a-fA-F]{64})\s+\*?" + re.escape(filename))
        hashes = [m[1].lower() for line in checksums if (m := pattern.fullmatch(line))]
        if len(hashes) != 1:
            raise ValueError(f"체크섬 항목 확인 필요: {filename}")
        archive = archive_dir / filename
        with archive.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if hashes[0] != actual:
            raise ValueError(f"체크섬 불일치: {filename}")
        with zipfile.ZipFile(archive) as zipped:
            fonts = sorted(n for n in zipped.namelist() if n.lower().endswith(".ttf"))
            expected = sorted(re.findall(r'^  font "([^"]+)"$', content, re.MULTILINE))
            if len(fonts) != 14 or fonts != expected:
                raise ValueError(f"TTF 구성이 변경됐습니다. Cask 경로를 검토하세요: {filename}")
            bad = zipped.testzip()
            if bad:
                raise ValueError(f"손상된 ZIP 항목: {bad}")
        substitutions = [
            (r'^  version "[^"]+"$', f'  version "{version}"'),
            (r'^  sha256 "[^"]+"$', f'  sha256 "{actual}"'),
            (
                r'^  url "[^"]+"$',
                f'  url "https://github.com/{repository}/releases/download/v#{{version}}/'
                f'Monatendard-v#{{version}}-{kind}.zip"',
            ),
        ]
        for pattern, replacement in substitutions:
            content, count = re.subn(
                pattern, lambda _, value=replacement: value, content, flags=re.MULTILINE
            )
            if count != 1:
                raise ValueError(f"Cask 항목 확인 필요: {path}: {pattern}")
        updates[path] = content
    return version, updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("repository는 owner/name 형식이어야 합니다.")
    if args.tag:
        stable_version(args.tag)
    endpoint = f"repos/{args.repository}/releases/" + (f"tags/{args.tag}" if args.tag else "latest")
    release = json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))
    version = stable_version(release["tag_name"])
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("초안 또는 사전 릴리스는 배포하지 않습니다.")
    with tempfile.TemporaryDirectory(prefix="monatendard-release-") as directory:
        subprocess.run(
            [
                "gh",
                "release",
                "download",
                release["tag_name"],
                "--repo",
                args.repository,
                "--dir",
                directory,
                "--pattern",
                f"Monatendard-v{version}-Desktop*.zip",
                "--pattern",
                "SHA256SUMS.txt",
            ],
            check=True,
        )
        version, updates = prepare_updates(ROOT, args.repository, release, Path(directory))
    changed = any(path.read_text(encoding="utf-8") != content for path, content in updates.items())
    for path, content in updates.items():
        path.write_text(content, encoding="utf-8")
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"version={version}\nchanged={str(changed).lower()}\n")
    print(f"검증 완료: {args.repository} v{version}; Cask 변경: {changed}")


if __name__ == "__main__":
    main()
