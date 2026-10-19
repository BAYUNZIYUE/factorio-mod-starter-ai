# 工作流说明

**简体中文** | [English](README.en.md)

本目录包含两个 GitHub Actions 工作流。

## `verify.yml`

在 push 到 `main` 和 pull request 时运行，不接触任何 Secret：

1. `python3 verify_mod.py` 校验所有模组源码（没有任何模组时 CI 直接失败）
2. 打包仓库中的真实模组；若只有 `example-mod`，则用它做冒烟打包
3. `python3 verify_mod.py --zip-dir dist` 校验 zip 结构

## `publish-to-mod-portal.yml`

分两个 job：

### `package`（始终运行）

1. checkout：release 事件检出 **tag 指向的提交**；手动触发检出所选分支
2. release 事件：解析 tag，校验 `<mod-name>-v<major.minor.patch>` 格式
3. release 事件：`verify_mod.py --target <mod> --tag <tag>` 校验目录名、`info.json`、tag 三者一致；手动触发：校验 `target_mod`（及可选 `version`），不传 `--tag`
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
- prerelease 不会触发上传；把 prerelease 改成正式 release 会触发 `released`（workflow 已订阅），重新运行并上传

### 2. 手动触发

在 GitHub Actions 页面点击 **Run workflow**：

| 输入 | 作用 |
|---|---|
| `target_mod` | 必填，只处理该模组目录 |
| `confirm` | 留空 = 只打包（dry-run）；输入 `PUBLISH` 才上传 |

> dry-run 的确切含义：`publish` job **完全不运行**——不查询 Mod Portal、不需要
> `FACTORIO_TOKEN`、不执行发布脚本；zip 仍会作为 GitHub Actions artifact 保留。
> 它不会验证 token/scope。Actions 显示绿色也可能是 `publish` job 被跳过。

`confirm=PUBLISH` 时还必须提供 `version`，且必须与 `src/info.json` 一致。

`example-mod` 在 `package` 阶段的 meta 校验中就会被拒绝（即使 `confirm` 留空、只想 dry-run 也不行）。本地 `TARGET_MOD=example-mod python3 pack_mods.py` 仅用于打包查看产物。

## 审批与并发

- `publish` job 使用 `environment: mod-portal-production`；请在仓库 Settings →
  Environments 中为它配置 required reviewers
- **未配置 required reviewers 时，GitHub 会自动创建该 environment 且没有审批**：
  release 一创建就会直接发布。配置后，release 与手动触发都会暂停等待批准
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
