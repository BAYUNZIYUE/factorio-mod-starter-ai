# 工作流说明

**简体中文** | [English](README.en.md)

本目录包含两个 GitHub Actions 工作流。

## `verify.yml`

在 push 到 `main` 和 pull request 时运行，不接触任何 Secret：

1. `python3 verify_mod.py` 校验所有模组源码
2. 打包 `example-mod` 作为冒烟测试
3. `python3 verify_mod.py --zip-dir dist` 校验 zip 结构

## `publish-to-mod-portal.yml`

分两个 job：

### `package`（始终运行）

1. checkout：release 事件检出 **tag 指向的提交**；手动触发检出所选分支
2. 解析 tag，校验 `<mod-name>-v<major.minor.patch>` 格式
3. `verify_mod.py --target <mod> --tag <tag>` 校验目录名、`info.json`、tag 三者一致
4. 打包到 `dist/`
5. 校验 zip 结构
6. 上传 artifact

### `publish`（仅在上传条件满足时运行）

1. 下载 artifact
2. `scripts/publish_mod.py` 查询 Mod Portal：
   - 模组不存在 → `init_publish`（scope `ModPortal: Publish Mods`）
   - 模组已存在 → `releases/init_upload`（scope `ModPortal: Upload Mods`）
3. 版本已存在则跳过（幂等，重跑安全）
4. 上传后再次查询 releases，确认版本可见

## 触发方式

### 1. Release 触发

创建并发布（非 prerelease）GitHub Release 时自动发布。要求：

- tag 格式：`<mod-name>-v<major.minor.patch>`
- tag 版本与 `src/info.json` 的 `version` 一致
- prerelease 不会触发上传

### 2. 手动触发

在 GitHub Actions 页面点击 **Run workflow**：

| 输入 | 作用 |
|---|---|
| `target_mod` | 必填，只处理该模组目录 |
| `confirm` | 留空 = 只打包（dry-run）；输入 `PUBLISH` 才上传 |

`example-mod` 会被拒绝，不能通过手动触发发布。

## 审批与并发

- `publish` job 使用 `environment: mod-portal-production`；请在仓库 Settings →
  Environments 中为它配置 required reviewers
- `concurrency` 全局串行，避免两个发布任务同时操作 Mod Portal

## 关键依赖

- `pack_mods.py`、`verify_mod.py`、`scripts/publish_mod.py`
- GitHub Secret `FACTORIO_TOKEN`（按用途授予 `Publish Mods` / `Upload Mods`）
- 模组结构 `<mod-name>/src/info.json`

## 风险提醒

- 配置真实 `FACTORIO_TOKEN` 后，release 会真实发布；Mod Portal 版本不可删除
- 不要用 release/tag 做配置测试；本地用 `verify_mod.py` + `pack_mods.py`
- 发布前阅读 `docs/PUBLISHING.md` 与 `docs/SECURITY_AND_PITFALLS.md`

## 相关文档

- [发布流程](../../docs/PUBLISHING.md)
- [安全与踩坑总结](../../docs/SECURITY_AND_PITFALLS.md)
- [AI 协作规则](../AI_RULES.md)
