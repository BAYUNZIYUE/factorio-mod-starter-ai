#!/usr/bin/env python3
"""Package every mod under the repository root into ready-to-publish zips."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from mod_utils import (
    EXAMPLE_MOD,
    iter_mod_dirs,
    iter_packable_files,
    validate_mod_dir,
    write_zip,
)

DEFAULT_OUTPUT_DIR = "dist"


def parse_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def resolve_output_dir(repo_root: Path) -> Path:
    configured = os.getenv("MOD_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    output = Path(configured)
    if not output.is_absolute():
        output = repo_root / output
    return output.resolve()


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    output_dir = resolve_output_dir(repo_root)

    target_mod = os.getenv("TARGET_MOD", "").strip()
    include_example = target_mod == EXAMPLE_MOD or parse_bool(
        os.getenv("INCLUDE_EXAMPLE")
    )

    mod_dirs = iter_mod_dirs(repo_root, include_example=include_example)
    if target_mod:
        mod_dirs = [d for d in mod_dirs if d.name == target_mod]
        if not mod_dirs:
            print(f"错误: 未找到模组 '{target_mod}'", file=sys.stderr)
            return 1
        print(f"只打包指定模组: {target_mod}")
    elif not mod_dirs:
        print("未找到任何模组目录（需要存在 <mod>/src/info.json）", file=sys.stderr)
        print(
            f"提示: 模板自带的 {EXAMPLE_MOD}/ 默认不参与打包；"
            f"可用 TARGET_MOD={EXAMPLE_MOD} python3 pack_mods.py 打包示例。",
            file=sys.stderr,
        )
        return 1
    else:
        print(f"发现 {len(mod_dirs)} 个模组目录，打包全部")

    for mod_dir in mod_dirs:
        src_dir = (mod_dir / "src").resolve()
        if output_dir == src_dir or src_dir in output_dir.parents:
            print(
                f"错误: 输出目录 {output_dir} 位于 {src_dir} 内；"
                "请把 MOD_OUTPUT_DIR 指到所有模组的 src/ 之外",
                file=sys.stderr,
            )
            return 1

    # Validate everything (including file collection) before writing anything:
    # a half-written release set is worse than a clean failure.
    plans = []
    failed = False
    for mod_dir in mod_dirs:
        check = validate_mod_dir(mod_dir)
        for warning in check.warnings:
            print(f"警告: {warning}")
        for error in check.errors:
            print(f"错误: {error}", file=sys.stderr)
            failed = True

        files, errors = iter_packable_files(mod_dir / "src", mod_dir)
        for error in errors:
            print(f"错误: {error}", file=sys.stderr)
            failed = True

        plans.append((check, files))

    if failed:
        print("校验失败，未生成任何 zip。", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    archives: list[Path] = []
    for check, files in plans:
        assert check.info is not None
        archive = write_zip(
            check.mod_dir,
            check.info,
            output_dir,
            files=files,
            changelog=check.changelog,
        )
        archives.append(archive)
        print(f"已打包: {check.mod_dir.name} -> {archive}")

    print(f"完成: {len(archives)} 个 zip 已写入 {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
