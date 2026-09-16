"""릴리스 자산 검증 실패 시 Cask 갱신이 게시되지 않도록 검사한다."""

import hashlib
import re
import runpy
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPDATER = runpy.run_path(str(ROOT / "packaging/macos/update_casks.py"))


@pytest.fixture
def release_files(tmp_path):
    (tmp_path / "Casks").mkdir()
    archives = tmp_path / "downloads"
    archives.mkdir()
    checksums = []
    for token, kind in UPDATER["PACKAGES"].items():
        text = (ROOT / "Casks" / f"{token}.rb").read_text()
        text = re.sub(r'^  version "[^"]+"$', '  version "0.2.2"', text, flags=re.M)
        (tmp_path / "Casks" / f"{token}.rb").write_text(text)
        archive = archives / f"Monatendard-v0.2.3-{kind}.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            for font in re.findall(r'^  font "([^"]+)"$', text, re.M):
                zipped.writestr(font, b"test-font")
        checksums.append(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}")
    (archives / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n")
    return tmp_path, {"tag_name": "v0.2.3", "draft": False, "prerelease": False}, archives


def prepare(files):
    root, release, archives = files
    return UPDATER["prepare_updates"](root, "younjungpark/Monatendard", release, archives)


def test_update_and_no_change(release_files):
    version, updates = prepare(release_files)
    assert version == "0.2.3"
    assert len(updates) == 2
    for path, content in updates.items():
        assert 'version "0.2.3"' in content
        assert 'url "https://github.com/younjungpark/Monatendard/releases/download/' in content
        assert "verified:" not in content
        assert 'version "0.2.2"' in path.read_text()  # 검증 중에는 파일을 쓰지 않음
        path.write_text(content)
    assert prepare(release_files)[1] == updates


def test_checksum_failure_leaves_both_files_unchanged(release_files):
    root, _, archives = release_files
    before = {path: path.read_bytes() for path in (root / "Casks").glob("*.rb")}
    with (archives / "Monatendard-v0.2.3-Desktop-Nerd.zip").open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(ValueError, match="체크섬 불일치"):
        prepare(release_files)
    assert all(path.read_bytes() == contents for path, contents in before.items())


def test_unexpected_font_path(release_files):
    root, _, _ = release_files
    path = root / "Casks/font-monatendard.rb"
    path.write_text(path.read_text().replace("fonts/Monatendard-Bold.ttf", "fonts/missing.ttf"))
    with pytest.raises(ValueError, match="TTF 구성"):
        prepare(release_files)


def test_duplicate_checksum(release_files):
    _, _, archives = release_files
    path = archives / "SHA256SUMS.txt"
    path.write_text(path.read_text() * 2)
    with pytest.raises(ValueError, match="체크섬 항목"):
        prepare(release_files)


def test_downgrade(release_files):
    root, _, _ = release_files
    path = root / "Casks/font-monatendard.rb"
    path.write_text(path.read_text().replace('version "0.2.2"', 'version "0.2.4"'))
    with pytest.raises(ValueError, match="버전 역행"):
        prepare(release_files)


@pytest.mark.parametrize("field", ["draft", "prerelease"])
def test_non_stable_release(release_files, field):
    release_files[1][field] = True
    with pytest.raises(ValueError, match="초안 또는 사전 릴리스"):
        prepare(release_files)


@pytest.mark.parametrize("tag", ["v0.2.3-beta.1", "v01.2.3", "--help", "v0.2.3\n"])
def test_invalid_tag(tag):
    with pytest.raises(ValueError, match="정식 버전"):
        UPDATER["stable_version"](tag)
