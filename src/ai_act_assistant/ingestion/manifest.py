import re
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Raised when the source manifest is missing or invalid."""


@dataclass(frozen=True, slots=True)
class SourceManifest:
    celex: str
    public_url: str
    download_url: str
    accept_header: str
    accept_language: str
    expected_sha256: str
    raw_path: Path


def load_manifest(path: Path) -> SourceManifest:
    """Load a source manifest from a TOML file."""
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except FileNotFoundError as error:
        raise ConfigError(f"Manifest file {path} does not exist.") from error
    except OSError as error:
        raise ConfigError(f"Could not open manifest file {path}: {error}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"Invalid TOML in manifest file {path}: {error}") from error

    try:
        expected_sha256 = data["snapshot"]["sha256"]
        if not isinstance(expected_sha256, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", expected_sha256
        ):
            raise ConfigError(
                "snapshot.sha256 must be a 64-character hexadecimal string."
            )
        expected_sha256 = expected_sha256.lower()

        return SourceManifest(
            celex=data["document"]["celex"],
            public_url=data["document"]["citation"]["public_url"],
            download_url=data["acquisition"]["download_url"],
            accept_header=data["acquisition"]["accept"],
            accept_language=data["acquisition"]["accept_language"],
            expected_sha256=expected_sha256,
            # local_path is relative to the project working directory.
            raw_path=Path(data["snapshot"]["local_path"]),
        )
    except KeyError as error:
        raise ConfigError(f"Missing required field in manifest: {error}") from error
