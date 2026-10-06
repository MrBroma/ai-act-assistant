from pathlib import Path

import pytest

from ai_act_assistant.ingestion.manifest import (
    ConfigError,
    SourceManifest,
    load_manifest,
)

VALID_MANIFEST = """
[document]
celex = "CELEX-123456"

[document.citation]
public_url = "https://example.com/public"

[acquisition]
download_url = "https://example.com/download"
accept = "text/html"
accept_language = "en-US"

[snapshot]
sha256 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
local_path = "data/raw_file.txt"
"""


def write_manifest(tmp_path: Path, content: str = VALID_MANIFEST) -> Path:
    path = tmp_path / "source.toml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_manifest(tmp_path: Path):
    manifest = load_manifest(write_manifest(tmp_path))

    assert isinstance(manifest, SourceManifest)
    assert manifest.celex == "CELEX-123456"
    assert manifest.public_url == "https://example.com/public"
    assert manifest.download_url == "https://example.com/download"
    assert manifest.accept_header == "text/html"
    assert manifest.accept_language == "en-US"
    assert manifest.expected_sha256 == (
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    assert manifest.raw_path == Path("data/raw_file.txt")


def test_load_manifest_missing_file(tmp_path: Path):
    with pytest.raises(ConfigError, match="does not exist"):
        load_manifest(tmp_path / "non_existent.toml")


def test_load_manifest_invalid_toml(tmp_path: Path):
    with pytest.raises(ConfigError, match="Invalid TOML"):
        load_manifest(write_manifest(tmp_path, "[document\ncelex = 'broken'"))


def test_load_manifest_missing_field(tmp_path: Path):
    content = VALID_MANIFEST.replace('celex = "CELEX-123456"', "")
    with pytest.raises(ConfigError, match="Missing required field"):
        load_manifest(write_manifest(tmp_path, content))


@pytest.mark.parametrize("sha256", ["", "abc123", "g" * 64, "a" * 63])
def test_load_manifest_invalid_sha256(tmp_path: Path, sha256: str):
    content = VALID_MANIFEST.replace(
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        sha256,
    )
    with pytest.raises(ConfigError, match="snapshot.sha256"):
        load_manifest(write_manifest(tmp_path, content))


def test_load_manifest_normalizes_uppercase_sha256(tmp_path: Path):
    content = VALID_MANIFEST.replace(
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF",
    )

    manifest = load_manifest(write_manifest(tmp_path, content))

    assert manifest.expected_sha256 == (
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )


def test_load_real_source_manifest():
    project_root = Path(__file__).parents[2]
    manifest = load_manifest(project_root / "configs/source.toml")

    assert manifest.celex == "02024R1689-20260727"
    assert manifest.accept_header == "application/xhtml+xml"
    assert manifest.accept_language == "eng"
    assert manifest.raw_path == Path("data/raw/ai_act_02024R1689-20260727_eng.xhtml")


def test_load_manifest_directory_path(tmp_path: Path):
    with pytest.raises(ConfigError):
        load_manifest(tmp_path)
