#!/usr/bin/env python3
"""Publish packaged mods to the Factorio Mod Portal.

Handles both first-time publishing (init_publish) and new releases of an
existing mod (releases/init_upload), which are two different API endpoints.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# Allow running as `python3 scripts/publish_mod.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_utils import parse_tag  # noqa: E402

API_BASE = "https://mods.factorio.com/api"
USER_AGENT = "factorio-mod-starter-ai"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3


def request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes]:
    """Perform an HTTP request with retries for transient failures."""
    merged = {"User-Agent": USER_AGENT}
    if headers:
        merged.update(headers)

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = urllib.request.Request(url, data=data, headers=merged, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if exc.code in RETRYABLE_STATUS and attempt < MAX_ATTEMPTS:
                time.sleep(2 ** attempt)
                continue
            return exc.code, body
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"请求失败: {url}: {exc}") from exc

    raise RuntimeError(f"请求失败: {url}: {last_error}")


def multipart(fields: dict[str, str], file_field: tuple[str, Path] | None = None) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    chunks: list[bytes] = []

    for key, value in fields.items():
        chunks.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n".encode()
        )

    if file_field is not None:
        field_name, path = file_field
        chunks.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field_name}"; filename="{path.name}"\r\n'
            "Content-Type: application/zip\r\n\r\n".encode()
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def get_mod(name: str) -> tuple[bool, list[str]]:
    status, body = request(f"{API_BASE}/mods/{name}/full")
    if status == 404:
        return False, []
    if status != 200:
        raise RuntimeError(
            f"查询模组 {name} 失败: HTTP {status}: {body[:300].decode(errors='replace')}"
        )
    payload = json.loads(body.decode("utf-8"))
    releases = payload.get("releases", [])
    versions = [str(item.get("version")) for item in releases if item.get("version")]
    return True, versions


def publish_one(archive: Path, token: str, *, dry_run: bool) -> None:
    stem = archive.stem
    if "_" not in stem:
        raise RuntimeError(f"{archive.name}: 文件名必须是 <name>_<version>.zip")
    name, version = stem.rsplit("_", 1)
    if name == "example-mod":
        raise RuntimeError(f"{archive.name}: 拒绝发布模板示例模组 example-mod")

    exists, versions = get_mod(name)
    if version in versions:
        print(f"SKIP  {name} {version} 已存在于 Mod Portal，跳过（幂等）")
        return

    endpoint = (
        f"{API_BASE}/v2/mods/releases/init_upload"
        if exists
        else f"{API_BASE}/v2/mods/init_publish"
    )
    action = "新版本" if exists else "首次发布"
    print(f"PLAN  {action}: {name} {version} -> {endpoint}")

    if dry_run:
        return

    payload, content_type = multipart({"mod": name})
    status, body = request(
        endpoint,
        method="POST",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
    )
    if status != 200:
        raise RuntimeError(
            f"{name}: init 请求失败 HTTP {status}: "
            f"{body[:500].decode(errors='replace')}"
        )

    init_payload = json.loads(body.decode("utf-8"))
    upload_url = init_payload.get("upload_url")
    if not upload_url:
        raise RuntimeError(f"{name}: 响应缺少 upload_url: {init_payload}")

    upload_payload, upload_content_type = multipart({}, ("file", archive))
    status, body = request(
        upload_url,
        method="POST",
        data=upload_payload,
        headers={"Content-Type": upload_content_type},
    )
    if status != 200:
        raise RuntimeError(
            f"{name}: 上传失败 HTTP {status}: {body[:500].decode(errors='replace')}"
        )

    result = json.loads(body.decode("utf-8"))
    if not result.get("success"):
        raise RuntimeError(f"{name}: 上传失败: {result}")

    # Verify the release is actually visible before reporting success.
    _, after = get_mod(name)
    if version not in after:
        raise RuntimeError(
            f"{name}: 上传返回成功，但 {version} 未出现在 releases 中"
        )

    print(f"OK    {name} {version} 已发布")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip-dir", type=Path, default=Path("dist"))
    parser.add_argument("--tag", help="release tag; only publish the matching mod/version")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.getenv("FACTORIO_TOKEN", "").strip()
    if not token:
        print("错误: 未设置 FACTORIO_TOKEN", file=sys.stderr)
        return 1

    archives = sorted(args.zip_dir.glob("*.zip"))
    if not archives:
        print(f"错误: {args.zip_dir} 中没有 zip", file=sys.stderr)
        return 1

    if args.tag:
        tag_name, tag_version = parse_tag(args.tag)
        archives = [
            a for a in archives
            if a.stem == f"{tag_name}_{tag_version}"
        ]
        if not archives:
            print(
                f"错误: 没有与 tag {args.tag} 匹配的 zip "
                f"（期望 {tag_name}_{tag_version}.zip）",
                file=sys.stderr,
            )
            return 1

    failed = False
    for archive in archives:
        try:
            publish_one(archive, token, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001 - report and continue with other mods
            print(f"FAIL  {archive.name}: {exc}", file=sys.stderr)
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
