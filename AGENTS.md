# AGENTS.md - Factorio Mod Template Repository Rules

**简体中文** | [English](AGENTS.en.md)

本文件是 `factorio-mod-starter-ai` 的项目级持久记忆。这是一个 **Factorio 模组开发模板仓库**，用于帮助开发者通过 AI 辅助完成 Factorio 模组开发与自动发布。新会话进入仓库后，应先读本文件，再读 `.github/AI_RULES.md` 与 `docs/` 下的文档。

## 项目概述

这是一个 **Factorio 模组开发模板仓库**，不是具体的模组项目。

提供：
- 完整的多模组工作区结构
- 自动打包脚本（`pack_mods.py`）和 GitHub Actions 发布流程
- AI 协作规范（`.github/AI_RULES.md`）与仓库边界规则（本文件）
- 开发指南和最佳实践文档（`docs/`）
- 双语支持（中/英文文档、README、贡献指南）

使用此模板创建新项目时，克隆仓库后删掉 `example-mod/` 即可开始开发。

## 技术栈

- Factorio 2.0 模组开发，模组代码以 Lua 为主，目录约定允许 `*.lua` / `*.ts` 入口
- Python 3 打包脚本：`pack_mods.py`
- GitHub Actions：`.github/workflows/publish-to-mod-portal.yml`（自动发布到 Mod Portal）
- 文档格式：Markdown（中/英文双语）

## Packaging Boundary

- 只有仓库根目录下、且包含 `src/info.json` 的目录，才视为正式可打包模组
- 打包入口脚本是仓库根目录的 `pack_mods.py`
- 打包输出目录默认为 `/home/factorio-mod-zips/`，可通过 `MOD_OUTPUT_DIR` 环境变量自定义
- 示例模组 `example-mod/` 仅供参考，实际使用时应删除或替换

## Required Mod Layout

每个正式模组都应采用：

```text
<mod-name>/
├── README.md
└── src/
    ├── info.json
    ├── control.lua / control.ts
    ├── data.lua / data.ts
    ├── settings.lua / settings.ts
    ├── settings-updates.lua / settings-final-fixes.lua
    ├── data-updates.lua / data-final-fixes.lua
    ├── locale/
    ├── scripts/
    ├── prototypes/
    └── changelog.txt
```

## 架构引导

- `pack_mods.py` 会扫描仓库根目录下所有包含 `src/info.json` 的目录，将其视为正式可打包模组
- 正式模组必须位于仓库根目录，采用 `<mod-name>/src/` 结构；目录名应与 `src/info.json` 中的 `name` 一致
- `example-mod/` 是模板自带的示例，展示完整的 `<mod>/src/` 结构和最小可运行入口文件
- 模板本身不包含实际模组业务代码；用户克隆后删除 `example-mod/`，按 `<mod-name>/src/info.json` 结构创建自己的模组
- `.github/workflows/publish-to-mod-portal.yml` 负责自动发布；`.github/AI_RULES.md` 是 AI 协作的强制规范

## Factorio Stage Boundaries

**关键约束（违反会导致运行时错误）：**

- `settings*`：只定义设置项（`data:extend` 设置原型）
- `data*`：只处理 `data:extend`、`data.raw`、原型定义与修改
- `control.lua` / `scripts/`：只处理运行时 API，如 `script`、`game`、`defines`
- **禁止在 `data` 阶段使用运行时 API**（如 `game`、`script`）
- **禁止在 `control` 阶段操作 `data.raw`**

**为什么这很重要：**
- Factorio 在不同阶段加载不同的 API
- `data` 阶段只有原型定义 API，没有游戏运行时 API
- `control` 阶段只有运行时 API，无法修改原型
- 违反边界会导致 `nil` 错误或模组加载失败

## Development Rules

- 玩家可见文本必须同步维护到 `locale/`
- 新增设置时同步补 `mod-setting-name` 与 `mod-setting-description`
- 原型标识改动时，必须检查是否需要 `migrations/`
- `control.lua` 应尽量薄，复杂运行时逻辑拆到 `scripts/`
- 变更要优先考虑旧存档兼容与多人同步安全

## 构建 & 验证

- 打包全部模组：`python3 pack_mods.py`
- 打包单个模组：`TARGET_MOD="<mod-name>" python3 pack_mods.py`
- `info.json` 必需字段：`name`、`version`、`factorio_version`、`title`、`author`、`description`
- 每个模组至少需要一个入口文件（`control`/`data`/`settings`）才能成功打包
- 修改模组结构、打包脚本或发布流程后，至少重新验证一次打包

## 项目内工具

- `pack_mods.py`：统一打包入口；默认输出目录取 `MOD_OUTPUT_DIR`，未设置时为 `/home/factorio-mod-zips`；也支持 `TARGET_MOD` 单模组打包
- `.github/workflows/publish-to-mod-portal.yml`：在 GitHub Release 创建时自动打包并发布到 Factorio Mod Portal
- `.github/AI_RULES.md`：AI 助手必须遵守的强制性规范，包含 tag 格式、API 端点、目录结构等不可修改项
- `docs/SETUP.md`：从零配置开发环境的完整指南
- `docs/MOD_DEVELOPMENT.md`：模组开发规范、目录结构、命名规则
- `docs/PUBLISHING.md`：手动与自动发布模组的详细流程
- `docs/TROUBLESHOOTING.md`：常见问题排查指南

## 环境配置

- `TARGET_MOD`：指定只打包某一个模组；为空时打包全部正式模组
- `MOD_OUTPUT_DIR`：打包输出目录；脚本默认值为 `/home/factorio-mod-zips`
- `FACTORIO_TOKEN`：发布到 Mod Portal 所需的 API Key（在 https://factorio.com/profile 生成，勾选 `ModPortal: Publish Mods`），配置为 GitHub Secret
- CI 环境打包输出约定为 `dist/`，本地开发约定为 `/home/factorio-mod-zips/`

## 约定 & 规范

- 文档优先级：`.github/AI_RULES.md` > `CONTRIBUTING.md` > `README.md` > 本文件
- 发布 tag 格式固定为 `<mod-name>-v<version>`，不要改动
- 发布 API 端点固定为 `https://mods.factorio.com/api/v2/mods/init_publish`，不要改成 `init_upload`
- 已定义环境变量名称 `TARGET_MOD`、`MOD_OUTPUT_DIR`、`FACTORIO_TOKEN` 不要改名
- `settings*` 只定义设置；`data*` 只处理原型与 `data.raw`；`control.lua` / `scripts/` 只处理运行时 API
- 玩家可见文本要同步维护到 `locale/`；新增设置时同步补 `mod-setting-name` 与 `mod-setting-description`
- 不要把 zip、日志、截图、临时脚本直接堆在仓库根目录；产物和调试输出优先放到 `artifacts/` 或 `dist/`
- 本地缓存目录如 `.local/`、`.sisyphus/`、`.codex/` 不应成为正式产物的一部分

## 已知问题 & 决策记录

- `example-mod/` 是模板自带的示例模组，不是正式交付内容。它用于展示结构，用户克隆后应删除或替换为自己的模组
- 打包输出目录在本地（`/home/factorio-mod-zips/`）与 CI（`dist/`）不一致，这是有意为之：本地固定路径方便测试，CI 临时目录避免残留
- 双语文档（中文为主、英文翻译）采用独立文件方案（`*.en.md`）而非 i18n 目录，简化 GitHub 渲染和贡献流程
- 模板不含 headless smoke test 工作流，因为不同模组的验证需求差异大；需要 smoke test 的项目可参考 `Factorio-MOD` 仓库的 workflow 配置
