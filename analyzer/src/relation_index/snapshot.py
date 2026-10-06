import os
import stat
import subprocess
from pathlib import Path

from pathspec import GitIgnoreSpec

from .storage import digest

COLLECTOR_VERSION = "snapshot-v8"
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "build",
    "dist",
    ".relation-index",
    ".idea",
    ".gradle",
    "__pycache__",
    ".pytest_cache",
    "vendor",
    "antbuild",
}
SOURCE_LANGUAGE_DIRS = {"java", "kotlin", "groovy", "scala", "resources"}
SOURCE_SET_DIRS = {"main", "test", "it", "integrationTest", "dockerTest"}
SOURCE_PACKAGE_NAMES = {"build", "target", "vendor", "dist", "antbuild"}


def _is_source_package_path(relative: str) -> bool:
    """Keep source packages named like build outputs, including their children."""
    parts = Path(relative).parts
    return any(
        parts[index] == "src"
        and parts[index + 1] in SOURCE_SET_DIRS
        and parts[index + 2] in SOURCE_LANGUAGE_DIRS
        and any(part in SOURCE_PACKAGE_NAMES for part in parts[index + 3 :])
        for index in range(len(parts) - 3)
    )
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".java",
    ".kt",
    ".py",
    ".go",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
    ".properties",
    ".json",
    ".toml",
    ".gradle",
    ".kts",
    ".md",
    ".txt",
    ".sql",
    ".html",
    ".css",
    ".php",
    ".rb",
    ".rs",
    ".scala",
    ".swift",
    ".tf",
    ".vue",
}
# The Vul4J+ full-source snapshot includes two tracked trees of about 643 MB.
# Keep a bounded collector, but allow those intended source snapshots to be
# indexed without silently excluding them from the P1 condition.
MAX_FILE_BYTES = 5_000_000
MAX_TOTAL_BYTES = 700_000_000
MAX_FILES = 25_000

LANGUAGES = {
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".go": "go",
    ".gradle": "groovy",
    ".html": "html",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".php": "php",
    ".properties": "generic",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".scala": "scala",
    ".sql": "generic",
    ".swift": "swift",
    ".tf": "terraform",
    ".toml": "generic",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".vue": "generic",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
}


def language_for_path(path):
    return LANGUAGES.get(Path(path).suffix.lower(), "generic")


def secret_name(name):
    lower = name.lower()
    return (
        lower.startswith(".env")
        or lower
        in {
            "credentials",
            "credentials.json",
            "secrets.json",
            "secrets.yml",
            "secrets.yaml",
            "id_rsa",
            "id_ed25519",
        }
        or lower.endswith((".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"))
    )


def _io_path(path: Path) -> str:
    """Return a Windows extended-length path for filesystem calls.

    Python's pathlib/os calls can still hit MAX_PATH even when Git was configured
    for long paths. Keep normal Path objects for relative manifest paths, and
    only add the Windows prefix at the I/O boundary.
    """
    value = os.path.abspath(os.fspath(path))
    if os.name != "nt":
        return value
    if value.startswith("\\\\?\\"):
        return value
    if value.startswith("\\\\"):
        return "\\\\?\\UNC\\" + value[2:]
    return "\\\\?\\" + value


def _iterdir(folder: Path):
    # os.scandir accepts the extended-length path. Rebuild children from the
    # original folder so manifest-relative path handling stays platform-neutral.
    with os.scandir(_io_path(folder)) as entries:
        for entry in entries:
            yield folder / entry.name


def _read_text(path: Path, *, encoding, errors):
    with open(_io_path(path), encoding=encoding, errors=errors) as stream:
        return stream.read()


def collect(root: Path, store, checkpoint=lambda: None, on_file=None):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    internal_roots = {}
    for path, reason in (
        (store.settings.data_dir.resolve(), "data_store"),
        (store.settings.github_directory, "github_store"),
    ):
        try:
            relative = path.relative_to(root).as_posix()
            internal_roots[relative] = reason
        except ValueError:
            pass
    files, omitted = [], []
    total = 0
    processed_files = 0

    def visit(folder, inherited):
        nonlocal total, processed_files
        checkpoint()
        rules = list(inherited)
        for ignore_name in (".gitignore", ".relationignore"):
            ignore = folder / ignore_name
            try:
                ignore_mode = os.lstat(_io_path(ignore)).st_mode
            except FileNotFoundError:
                ignore_mode = 0
            if stat.S_ISREG(ignore_mode):
                rules.append(
                    (
                        folder,
                        GitIgnoreSpec.from_lines(
                            _read_text(ignore, encoding="utf-8", errors="replace").splitlines()
                        ),
                    )
                )
        for path in sorted(_iterdir(folder), key=lambda p: p.name):
            checkpoint()
            relative = path.relative_to(root).as_posix()
            mode = os.lstat(_io_path(path)).st_mode
            if path.name == ".relationignore":
                omitted.append({"path": relative, "reason": "control_file"})
                continue
            if stat.S_ISLNK(mode):
                omitted.append({"path": relative, "reason": "symlink"})
                continue
            directory = stat.S_ISDIR(mode)
            internal_reason = internal_roots.get(relative) if directory else None
            if internal_reason:
                omitted.append({"path": relative, "reason": internal_reason})
                continue
            ignored = False
            for base, spec in rules:
                match = spec.check_file(
                    path.relative_to(base).as_posix() + ("/" if directory else "")
                )
                if match.include is not None:
                    ignored = match.include
            source_package = _is_source_package_path(relative)
            if (
                (ignored and not source_package)
                or secret_name(path.name)
                or (
                    directory
                    and path.name in EXCLUDED_DIRS
                    and not (source_package and path.name in SOURCE_PACKAGE_NAMES)
                )
            ):
                omitted.append({"path": relative, "reason": "excluded"})
                continue
            if directory:
                visit(path, rules)
                continue
            if not stat.S_ISREG(mode):
                omitted.append({"path": relative, "reason": "not_regular"})
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {
                "Dockerfile",
                "Makefile",
                ".gitignore",
            }:
                omitted.append({"path": relative, "reason": "unsupported"})
                continue
            if os.stat(_io_path(path)).st_size > MAX_FILE_BYTES:
                omitted.append({"path": relative, "reason": "size"})
                continue
            processed_files += 1
            if on_file:
                on_file(processed_files, 0, relative)
            # O_NOFOLLOW also rejects a file replaced by a symlink after the directory scan.
            fd = os.open(_io_path(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                omitted.append({"path": relative, "reason": "size"})
                continue
            try:
                text = data.decode("utf-8")
                if "\x00" in text:
                    raise UnicodeError()
            except UnicodeError:
                omitted.append({"path": relative, "reason": "non_utf8_or_binary"})
                continue
            total += len(data)
            if total > MAX_TOTAL_BYTES or len(files) >= MAX_FILES:
                raise ValueError(
                    f"Snapshot exceeds the {MAX_FILES:,} file / {MAX_TOTAL_BYTES:,} byte limit"
                )
            files.append(
                {
                    "path": relative,
                    "hash": store.put_blob(data),
                    "size": len(data),
                    "language": language_for_path(relative),
                    "line_count": len(text.splitlines()),
                }
            )

    visit(root, [])
    commit = None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    manifest = {
        "collector_version": COLLECTOR_VERSION,
        "files": files,
        "omitted": omitted,
        "git_commit": commit,
    }
    manifest["content_hash"] = digest(
        {
            "version": COLLECTOR_VERSION,
            "files": files,
            "omitted": omitted,
            "git_commit": commit,
        }
    )
    return manifest
