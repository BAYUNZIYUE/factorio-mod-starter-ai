# AGENTS.md — Factorio Mod Starter AI

**简体中文** | [English](AGENTS.en.md)

本文件是仓库的唯一入口规则，保持简短。详细说明按需读 `docs/`，不要预加载全部文档。

## 这个仓库是什么

一个 **Factorio 模组开发模板**：多模组目录 + 打包脚本 + GitHub Actions 发布 + AI 协作约束。
它本身不是模组项目。用它创建项目后，保留 `AGENTS.md`（应提交），删除 `example-mod/`。

模板仓库与实例仓库的区别：

| 角色 | 位置 | 是否提交 |
|---|---|---|
| 项目规则 | `AGENTS.md` / `.github/AI_RULES.md` | 是 |
| 个人环境信息（本机路径、token、调试笔记） | `AGENTS.local.md`（若工具支持）或本地未跟踪文件 | 否 |
| 打包产物 | `dist/` | 否（已在 `.gitignore`） |

## 目录约定

```text
<mod-name>/
├── src/
│   ├── info.json              # 唯一必需文件
│   ├── control.lua            # 运行时；顶层只有 script/remote/commands
│   ├── data.lua               # 原型；data-updates.lua / data-final-fixes.lua
│   ├── settings.lua           # 设置；settings-updates.lua / settings-final-fixes.lua
│   ├── locale/<lang>/locale.cfg
│   ├── migrations/<mod-version>.lua   # 旧存档迁移，文件名是模组版本
│   ├── scripts/               # 运行时逻辑拆分
│   ├── prototypes/
│   ├── graphics/
│   └── changelog.txt          # 推荐，非必需
└── README.md
```

硬性规则：

- 目录名必须等于 `src/info.json` 的 `name`（小写字母/数字/`-`/`_`，3–50 字符）
- `version` 必须是 `major.minor.patch`；`factorio_version` 必须是两段式主版本（如 `"2.0"`）
- 入口只认 `.lua`。TypeScript 必须先用 TypeScriptToLua 编译为同名 `.lua`；模板不内置编译链
- 只打包 `src/` 下的文件；构建产物、临时文件、`.git`、`node_modules`、`__pycache__`、`.DS_Store` 会被排除
- `example-mod/` 默认不参与打包；显式 `TARGET_MOD=example-mod` 时才打包

## 阶段边界（违反会加载失败）

| 阶段 | 允许 | 禁止 |
|---|---|---|
| `settings*` | `data:extend` 设置原型、`settings.startup` | `game`、`script`、运行时 API |
| `data*` | `data:extend`、`data.raw`、原型定义/修改、`settings.startup` | `game`、`script`、`remote`、事件注册 |
| `control.lua` 顶层 | `script`、`remote`、`commands` | `game`、`rendering`、`data`（不存在） |
| 事件回调 / `on_init` / `on_configuration_changed` | 完整运行时 API、`game`、`rendering` | 修改原型（已锁定） |

存档加载顺序：`control.lua` → `on_init` → migrations → `on_load` → `on_configuration_changed` → 事件。
`on_load` 中不能访问 `game`；`data` 在 control 阶段不可访问，不是“只读”。

## 发布（高风险，不可逆）

Mod Portal **不提供删除已发布版本**的 API。发布前必须显式授权，禁止用 release/tag 做“测试”。

- tag 格式：`<mod-name>-v<major.minor.patch>`，版本必须与 `src/info.json` 一致
- 首次创建 mod：`POST /api/v2/mods/init_publish`，token scope `ModPortal: Publish Mods`
- 已有 mod 发新版本：`POST /api/v2/mods/releases/init_upload`，token scope `ModPortal: Upload Mods`
- workflow 会自动查询 mod 是否存在并选择端点；版本已存在时跳过（幂等）
- 发布 workflow 只在正式 release（非 prerelease）或手动输入 `PUBLISH` 时上传；手动触发必须指定 `target_mod`
- `FACTORIO_TOKEN` 只能放在 GitHub Secrets，禁止写入仓库、日志、截图

## 验证（完成标准）

```bash
python3 verify_mod.py                 # 源码：字段/名称/版本/入口/changelog
TARGET_MOD="<mod>" python3 pack_mods.py   # 打包到 dist/
python3 verify_mod.py --zip-dir dist  # zip：根目录/必需文件/垃圾文件/版本一致
```

只有以上命令全部通过，才算“改完”。CI 在 push/PR 时跑同一组检查（`.github/workflows/verify.yml`）。

## 禁止事项（没有明确授权时）

- 不创建 release、不推 tag、不触发远端发布
- 不把真实 token、密码、内部路径写入任何受版本控制的文件
- 不发布 `example-mod/`
- 不在 `data` 阶段使用运行时 API，不在 `control` 阶段访问 `data`
- 不把 `AGENTS.md` 加入 `.gitignore`（它是项目规则，应提交）

## 按需文档

| 需要什么 | 读哪里 |
|---|---|
| 从零配置 | `docs/SETUP.md` |
| 目录/命名/阶段细节 | `docs/MOD_DEVELOPMENT.md` |
| 发布流程与排错 | `docs/PUBLISHING.md` |
| 安全与误发布风险 | `docs/SECURITY_AND_PITFALLS.md` |
| 报错排查 | `docs/TROUBLESHOOTING.md` |
| 强制规范全文 | `.github/AI_RULES.md` |
| CI 行为 | `.github/workflows/README.md` |

## 已知决策

- 默认输出 `dist/`（不是固定绝对路径），本地与 CI 一致
- `example-mod/` 仅用于展示结构，默认排除发布
- 双语采用 `*.en.md` 独立文件，中文为 canonical；英文翻译滞后时以中文为准
- 模板不内置 headless smoke test；需要时用 `--mod-directory` + `--create`/`--dump-data` 或社区 FactorioTest
