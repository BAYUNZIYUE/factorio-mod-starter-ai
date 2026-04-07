from __future__ import annotations

import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT_DIR = Path(os.getenv("MOD_OUTPUT_DIR", "/home/factorio-mod-zips"))


REQUIRED_INFO_FIELDS = (
    "name",
    "version",
    "factorio_version",
    "title",
    "author",
    "description",
)

ENTRYPOINT_PREFIXES = ("control", "data", "settings")
ENTRYPOINT_SUFFIXES = (".lua", ".ts")


def iter_mod_dirs(repo_root: Path) -> list[Path]:
    mod_dirs: list[Path] = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if child.name in {"ModZips", "__pycache__", "scripts", "mods", "shared"}:
            continue
        if (child / "src" / "info.json").is_file():
            mod_dirs.append(child)
    return mod_dirs


def load_info(mod_dir: Path) -> dict[str, object]:
    info_path = mod_dir / "src" / "info.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_INFO_FIELDS if not info.get(field)]
    if missing:
        raise ValueError(f"{mod_dir.name}: info.json 缺少字段: {', '.join(missing)}")
    return info


def has_entrypoint(src_dir: Path) -> bool:
    for prefix in ENTRYPOINT_PREFIXES:
        for suffix in ENTRYPOINT_SUFFIXES:
            if (src_dir / f"{prefix}{suffix}").is_file():
                return True
    return False


def changelog_path(mod_dir: Path) -> Path | None:
    candidates = [mod_dir / "changelog.txt", mod_dir / "src" / "changelog.txt"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def package_mod(mod_dir: Path, output_dir: Path) -> Path:
    src_dir = mod_dir / "src"
    info = load_info(mod_dir)

    if not has_entrypoint(src_dir):
        raise ValueError(f"{mod_dir.name}: src/ 中缺少 control/data/settings 入口文件")

    mod_name = str(info["name"])
    version = str(info["version"])
    archive_root = f"{mod_name}_{version}"
    archive_path = output_dir / f"{archive_root}.zip"

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for file_path in sorted(src_dir.rglob("*")):
            if file_path.is_file():
                relative_path = file_path.relative_to(src_dir)
                zip_file.write(file_path, archive_root + "/" + relative_path.as_posix())

        extra_changelog = changelog_path(mod_dir)
        if extra_changelog is not None and extra_changelog.parent != src_dir:
            zip_file.write(extra_changelog, archive_root + "/changelog.txt")

    return archive_path


def main() -> int:
    import sys
    
    repo_root = Path(__file__).resolve().parent
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    target_mod = os.getenv("TARGET_MOD")
    
    mod_dirs = iter_mod_dirs(repo_root)
    if not mod_dirs:
        print("未找到任何模组目录（需要存在 <mod>/src/info.json）")
        return 1

    if target_mod:
        mod_dirs = [d for d in mod_dirs if d.name == target_mod]
        if not mod_dirs:
            print(f"错误: 未找到模组 '{target_mod}'")
            return 1
        print(f"只打包指定模组: {target_mod}")
    else:
        print(f"发现 {len(mod_dirs)} 个模组目录，打包全部")
    
    for mod_dir in mod_dirs:
        archive_path = package_mod(mod_dir, output_dir)
        print(f"已打包: {mod_dir.name} -> {archive_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
