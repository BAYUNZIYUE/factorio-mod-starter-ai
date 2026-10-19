#!/usr/bin/env python3
"""Verify mod sources and/or packaged zips. Exit code 1 means "do not publish"."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mod_utils import (
    EXAMPLE_MOD,
    iter_mod_dirs,
    parse_tag,
    validate_mod_dir,
    validate_zip,
)


def verify_sources(
    repo_root: Path, *, target: str | None, tag: str | None, allow_example: bool = True
) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []

    # The template's example mod is part of the repository and must stay valid,
    # even though pack_mods.py excludes it from publishing by default.
    include_example = allow_example or target == EXAMPLE_MOD
    mod_dirs = iter_mod_dirs(repo_root, include_example=include_example)
    if target:
        mod_dirs = [d for d in mod_dirs if d.name == target]
        if not mod_dirs:
            errors.append(f"未找到模组目录: {target}")

    if not mod_dirs and not errors:
        errors.append("未找到任何模组（需要 <mod>/src/info.json）")

    tag_name = tag_version = None
    if tag:
        try:
            tag_name, tag_version = parse_tag(tag)
        except ValueError as exc:
            errors.append(str(exc))

    for mod_dir in mod_dirs:
        check = validate_mod_dir(mod_dir)
        errors.extend(check.errors)
        warnings.extend(check.warnings)

        if check.info is not None and tag_name is not None:
            if tag_name != mod_dir.name:
                errors.append(
                    f"{mod_dir.name}: tag 中的模组名 {tag_name!r} "
                    f"与目录名 {mod_dir.name!r} 不一致"
                )
            if tag_version != str(check.info["version"]):
                errors.append(
                    f"{mod_dir.name}: tag 版本 {tag_version!r} "
                    f"与 info.json {check.info['version']!r} 不一致"
                )

        if check.ok:
            version = check.info["version"] if check.info else "?"
            print(f"OK  {mod_dir.name} {version}")

    return errors, warnings, len(mod_dirs)


def verify_zips(
    zip_dir: Path, *, target: str | None, tag: str | None
) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []

    if not zip_dir.is_dir():
        return [f"zip 目录不存在: {zip_dir}"], warnings, 0

    archives = sorted(zip_dir.glob("*.zip"))
    if not archives:
        return [f"{zip_dir} 中没有 zip 文件"], warnings, 0

    tag_name = tag_version = None
    if tag:
        try:
            tag_name, tag_version = parse_tag(tag)
        except ValueError as exc:
            errors.append(str(exc))

    checked = 0
    for archive in archives:
        name = archive.stem.rsplit("_", 1)[0] if "_" in archive.stem else archive.stem
        if target and name != target:
            continue
        checked += 1
        archive_errors = validate_zip(archive)
        errors.extend(archive_errors)

        if tag_name is not None:
            version = archive.stem.rsplit("_", 1)[-1]
            if name != tag_name:
                errors.append(
                    f"{archive.name}: zip 模组名 {name!r} 与 tag {tag_name!r} 不一致"
                )
            if version != tag_version:
                errors.append(
                    f"{archive.name}: zip 版本 {version!r} 与 tag {tag_version!r} 不一致"
                )

        if not archive_errors:
            print(f"OK  {archive.name}")

    if checked == 0:
        errors.append(f"没有与 target={target!r} 匹配的 zip")

    return errors, warnings, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", default=Path(__file__).resolve().parent, type=Path,
        help="repository root (default: script directory)",
    )
    parser.add_argument("--target", help="only verify this mod (directory name)")
    parser.add_argument("--tag", help="release tag, e.g. my-mod-v1.0.0")
    parser.add_argument("--zip-dir", type=Path, help="verify packaged zips in this directory")
    parser.add_argument(
        "--exclude-example", action="store_true",
        help=f"do not verify {EXAMPLE_MOD!r} during source verification",
    )
    args = parser.parse_args()

    if args.zip_dir is not None:
        errors, warnings, count = verify_zips(
            args.zip_dir, target=args.target, tag=args.tag
        )
        scope = f"{count} 个 zip"
    else:
        errors, warnings, count = verify_sources(
            args.root.resolve(),
            target=args.target,
            tag=args.tag,
            allow_example=not args.exclude_example,
        )
        scope = f"{count} 个模组"

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)

    if errors:
        print(f"校验失败（{scope}）：{len(errors)} 个错误", file=sys.stderr)
        return 1

    print(f"校验通过（{scope}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
