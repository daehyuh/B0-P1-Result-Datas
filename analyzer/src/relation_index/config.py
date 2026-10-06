import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    github_root: Path | None = None

    @classmethod
    def from_env(cls):
        data_dir = Path(os.environ.get("RELATION_DATA_DIR", ".relation-index")).expanduser().resolve()
        configured = os.environ.get("RELATION_GITHUB_ROOT")
        github_root = (
            Path(configured).expanduser().resolve() if configured else data_dir.parent / "github"
        )
        return cls(data_dir, github_root)

    @property
    def database(self):
        return self.data_dir / "relations.sqlite3"

    @property
    def github_directory(self):
        return (self.github_root or self.data_dir.parent / "github").expanduser().resolve()

    def initialize(self):
        for name in ("blobs", "parse_cache"):
            (self.data_dir / name).mkdir(parents=True, exist_ok=True)
