"""Shared validation and packaging helpers for the mod starter template.

This module is the single source of truth for what a valid mod looks like.
It is intentionally dependency-free (Python standard library only) so it can
run in CI without an install step.
"""

from __future__ import annotations

import json
import re
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

# Official mod name rules (Factorio mod structure): lowercase letters, digits,
# dashes and underscores, 3-50 characters.
NAME_RE = re.compile(r"^[a-z0-9_-]{3,50}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
FACTORIO_VERSION_RE = re.compile(r"^\d+\.\d+$")

REQUIRED_INFO_FIELDS = (
    "name",
    "version",
    "factorio_version",
    "title",
    "author",
    "description",
)

ENTRYPOINT_PREFIXES = ("control", "data", "settings")
# Factorio only loads .lua entrypoints. TypeScript must be compiled first.
ENTRYPOINT_SUFFIX = ".lua"

# Directories that must never be shipped inside a mod zip.
EXCLUDED_DIR_PARTS = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    ".pytest_cache",
}

EXCLUDED_FILE_NAMES = {".DS_Store", "Thumbs.db"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip", ".tsbuildinfo"}

# The template example must never be published by default. It can still be
# packaged on purpose with TARGET_MOD=example-mod.
EXAMPLE_MOD = "example-mod"

# Repo-root directories that are not mods even if they happen to contain
# src/info.json (kept for backwards compatibility with the old script).
RESERVED_DIRS = {"ModZips", "scripts", "mods", "shared"}

# Fixed timestamp makes zip output reproducible across machines/checkouts.
ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)
ZIP_FILE_MODE = (stat.S_IFREG | 0o644) << 16


@dataclass
class ModCheck:
    mod_dir: Path
    info: dict | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changelog: Path | None = None

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_tag(tag: str) -> tuple[str, str]:
    """Split '<mod-name>-v<major.minor.patch>' into (name, version)."""
    if "-v" not in tag:
        raise ValueError(f"非法 tag: {tag!r}（要求 <mod-name>-v<major.minor.patch>）")
    name, version = tag.rsplit("-v", 1)
    if not name:
        raise ValueError(f"非法 tag: {tag!r}（缺少模组名）")
    if not VERSION_RE.fullmatch(version):
        raise ValueError(
            f"非法 tag: {tag!r}（版本部分必须是 major.minor.patch，实际为 {version!r}）"
        )
    return name, version


def iter_mod_dirs(
    root: Path, *, include_example: bool = False
) -> list[Path]:
    """Return candidate mod directories (direct children with src/info.json)."""
    mod_dirs: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in RESERVED_DIRS:
            continue
        if child.name == EXAMPLE_MOD and not include_example:
            continue
        if (child / "src" / "info.json").is_file():
            mod_dirs.append(child)
    return mod_dirs


def load_info(mod_dir: Path) -> dict:
    info_path = mod_dir / "src" / "info.json"
    try:
        raw = info_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise ValueError(f"{mod_dir.name}: 缺少 src/info.json") from exc
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{mod_dir.name}: src/info.json 不是合法 JSON: {exc}") from exc
    if not isinstance(info, dict):
        raise ValueError(f"{mod_dir.name}: src/info.json 顶层必须是对象")
    return info


def changelog_path(mod_dir: Path) -> tuple[Path | None, str | None]:
    """Return (path, error). Rejects two changelogs because zip entries collide."""
    root_cl = mod_dir / "changelog.txt"
    src_cl = mod_dir / "src" / "changelog.txt"
    if root_cl.is_file() and src_cl.is_file():
        return None, (
            f"{mod_dir.name}: changelog.txt 同时存在于根目录和 src/，请只保留一处"
        )
    if src_cl.is_file():
        return src_cl, None
    if root_cl.is_file():
        return root_cl, None
    return None, None


def validate_changelog(path: Path, info: dict, check: ModCheck) -> None:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()

    dash_lines = [line for line in lines if set(line) == {"-"}]
    if not any(len(line) == 99 for line in dash_lines):
        check.warnings.append(
            f"{path.relative_to(check.mod_dir)}: 未找到 99 个短横线的分节线"
            "（Factorio changelog 格式要求）"
        )

    versions = [
        line.split(":", 1)[1].strip()
        for line in lines
        if line.startswith("Version:")
    ]
    if not versions:
        check.errors.append(f"{path.relative_to(check.mod_dir)}: 缺少 'Version:' 行")
    elif versions[0] != str(info["version"]):
        check.errors.append(
            f"{path.relative_to(check.mod_dir)}: 顶部版本 {versions[0]!r} "
            f"与 info.json {info['version']!r} 不一致"
        )

    if not any(line.startswith("Date:") for line in lines):
        check.warnings.append(f"{path.relative_to(check.mod_dir)}: 缺少 'Date:' 行")


def validate_info_fields(info: dict, label: str) -> list[str]:
    """Shared info.json field checks for both sources and packaged zips."""
    errors: list[str] = []

    missing = [f for f in REQUIRED_INFO_FIELDS if not info.get(f)]
    if missing:
        return [f"{label}: info.json 缺少字段: {', '.join(missing)}"]

    name = str(info["name"])
    version = str(info["version"])
    factorio_version = str(info["factorio_version"])

    if not NAME_RE.fullmatch(name):
        errors.append(
            f"{label}: 非法 mod name {name!r}"
            "（只允许小写字母、数字、-、_，长度 3-50）"
        )
    if not VERSION_RE.fullmatch(version):
        errors.append(
            f"{label}: 非法 version {version!r}（要求 major.minor.patch）"
        )
    if not FACTORIO_VERSION_RE.fullmatch(factorio_version):
        errors.append(
            f"{label}: 非法 factorio_version {factorio_version!r}"
            '（要求两段式主版本，如 "2.0"）'
        )

    deps = info.get("dependencies")
    if deps is not None and (
        not isinstance(deps, list) or not all(isinstance(d, str) for d in deps)
    ):
        errors.append(f"{label}: dependencies 必须是字符串数组")

    return errors


def validate_mod_dir(mod_dir: Path) -> ModCheck:
    check = ModCheck(mod_dir=mod_dir)

    try:
        info = load_info(mod_dir)
    except ValueError as exc:
        check.errors.append(str(exc))
        return check

    check.info = info

    field_errors = validate_info_fields(info, mod_dir.name)
    check.errors.extend(field_errors)
    if field_errors:
        return check

    name = str(info["name"])
    version = str(info["version"])

    if name != mod_dir.name:
        check.errors.append(
            f"{mod_dir.name}: 目录名与 info.json 的 name 不一致（name={name!r}）"
        )

    src_dir = mod_dir / "src"
    lua_entries = [
        src_dir / f"{prefix}{ENTRYPOINT_SUFFIX}" for prefix in ENTRYPOINT_PREFIXES
    ]
    if not any(path.is_file() for path in lua_entries):
        check.errors.append(
            f"{mod_dir.name}: src/ 中缺少 Lua 入口文件"
            "（control.lua / data.lua / settings.lua 至少一个）"
        )

    ts_files = sorted(
        p for p in src_dir.rglob("*.ts") if p.is_file()
    )
    if ts_files:
        missing_lua = [
            p.relative_to(mod_dir).as_posix()
            for p in ts_files
            if not p.with_suffix(".lua").is_file()
        ]
        if missing_lua:
            check.errors.append(
                f"{mod_dir.name}: 发现未编译的 TypeScript 文件: "
                f"{', '.join(missing_lua)}；请先用 TypeScriptToLua 生成同名 .lua"
            )
        else:
            check.warnings.append(
                f"{mod_dir.name}: 存在 .ts 源文件；请确认构建产物已同步更新"
            )

    cl_path, cl_error = changelog_path(mod_dir)
    if cl_error:
        check.errors.append(cl_error)
    elif cl_path is not None:
        check.changelog = cl_path
        validate_changelog(cl_path, info, check)

    return check


def iter_packable_files(src_dir: Path, mod_dir: Path) -> tuple[list[Path], list[str]]:
    """Return (files, errors) for zip creation, dropping junk and symlinks."""
    files: list[Path] = []
    errors: list[str] = []

    for path in sorted(src_dir.rglob("*")):
        rel = path.relative_to(src_dir)
        if path.is_symlink():
            errors.append(f"{mod_dir.name}: 不允许符号链接: {rel.as_posix()}")
            continue
        if path.is_dir():
            continue

        if any(part in EXCLUDED_DIR_PARTS for part in rel.parts):
            continue
        if rel.name in EXCLUDED_FILE_NAMES or rel.suffix in EXCLUDED_SUFFIXES:
            continue
        # TypeScript sources are build inputs, not runtime files. Factorio only
        # loads the compiled .lua output.
        if rel.suffix in {".ts", ".tsx"}:
            continue

        try:
            resolved = path.resolve()
            resolved.relative_to(mod_dir.resolve())
        except (OSError, ValueError):
            errors.append(f"{mod_dir.name}: 文件越出模组目录: {rel.as_posix()}")
            continue

        files.append(path)

    return files, errors


def write_zip(
    mod_dir: Path,
    info: dict,
    output_dir: Path,
    *,
    files: list[Path],
    changelog: Path | None,
) -> Path:
    name = str(info["name"])
    version = str(info["version"])
    archive_root = f"{name}_{version}"
    archive_path = output_dir / f"{archive_root}.zip"
    tmp_path = output_dir / f".{archive_root}.zip.tmp"

    src_dir = mod_dir / "src"

    def add(zf: ZipFile, source: Path, arcname: str) -> None:
        entry = ZipInfo(arcname, date_time=ZIP_DATE_TIME)
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = ZIP_FILE_MODE
        with source.open("rb") as src, zf.open(entry, "w") as dst:
            shutil.copyfileobj(src, dst)

    try:
        with ZipFile(tmp_path, "w", compression=ZIP_DEFLATED) as zf:
            for path in files:
                rel = path.relative_to(src_dir).as_posix()
                add(zf, path, f"{archive_root}/{rel}")

            if changelog is not None and changelog.parent != src_dir:
                add(zf, changelog, f"{archive_root}/changelog.txt")

        tmp_path.replace(archive_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return archive_path


def validate_zip(
    archive_path: Path,
    *,
    expected_name: str | None = None,
    expected_version: str | None = None,
) -> list[str]:
    """Return a list of errors for a packaged mod zip."""
    errors: list[str] = []

    stem = archive_path.stem
    if "_" not in stem:
        return [f"{archive_path.name}: 文件名必须是 <name>_<version>.zip"]
    name, version = stem.rsplit("_", 1)

    if expected_name is not None and name != expected_name:
        errors.append(
            f"{archive_path.name}: zip 名中的 name {name!r} 与预期 {expected_name!r} 不一致"
        )
    if expected_version is not None and version != expected_version:
        errors.append(
            f"{archive_path.name}: zip 名中的 version {version!r} "
            f"与预期 {expected_version!r} 不一致"
        )

    if not NAME_RE.fullmatch(name):
        errors.append(f"{archive_path.name}: 非法 mod name {name!r}")
    if not VERSION_RE.fullmatch(version):
        errors.append(f"{archive_path.name}: 非法 version {version!r}")

    archive_root = f"{name}_{version}"

    try:
        with ZipFile(archive_path) as zf:
            names = zf.namelist()
    except Exception as exc:  # noqa: BLE001 - report any corrupt zip as a check error
        return [f"{archive_path.name}: 无法读取 zip: {exc}"]

    if not names:
        return [f"{archive_path.name}: zip 为空"]

    for entry in names:
        if entry.startswith("/") or ".." in Path(entry).parts:
            errors.append(f"{archive_path.name}: 非法 zip 路径 {entry!r}")
        if not entry.startswith(archive_root + "/"):
            errors.append(
                f"{archive_path.name}: 条目 {entry!r} 不在根目录 {archive_root}/ 下"
            )
        parts = Path(entry).parts
        if any(part in EXCLUDED_DIR_PARTS for part in parts):
            errors.append(f"{archive_path.name}: 包含不应发布的目录 {entry!r}")
        if Path(entry).name in EXCLUDED_FILE_NAMES:
            errors.append(f"{archive_path.name}: 包含不应发布的文件 {entry!r}")

    info_entry = f"{archive_root}/info.json"
    if info_entry not in names:
        errors.append(f"{archive_path.name}: 缺少 {info_entry}")
    else:
        try:
            with ZipFile(archive_path) as zf:
                info = json.loads(zf.read(info_entry).decode("utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{archive_path.name}: info.json 无法解析: {exc}")
        else:
            if not isinstance(info, dict):
                errors.append(f"{archive_path.name}: info.json 顶层必须是对象")
            else:
                errors.extend(validate_info_fields(info, archive_path.name))
                if str(info.get("name")) != name:
                    errors.append(
                        f"{archive_path.name}: info.json name {info.get('name')!r} "
                        f"与文件名 {name!r} 不一致"
                    )
                if str(info.get("version")) != version:
                    errors.append(
                        f"{archive_path.name}: info.json version {info.get('version')!r} "
                        f"与文件名 {version!r} 不一致"
                    )

    lua_entries = {f"{archive_root}/{prefix}.lua" for prefix in ENTRYPOINT_PREFIXES}
    if not any(entry in names for entry in lua_entries):
        errors.append(
            f"{archive_path.name}: 缺少 Lua 入口"
            "（control.lua / data.lua / settings.lua 至少一个）"
        )

    ts_entries = [entry for entry in names if entry.endswith((".ts", ".tsx"))]
    if ts_entries:
        errors.append(
            f"{archive_path.name}: 包含未编译的 TypeScript 文件: "
            f"{', '.join(ts_entries)}"
        )

    changelog_entries = [n for n in names if n.endswith("/changelog.txt")]
    if len(changelog_entries) > 1:
        errors.append(
            f"{archive_path.name}: changelog.txt 出现 {len(changelog_entries)} 次"
        )

    return errors
