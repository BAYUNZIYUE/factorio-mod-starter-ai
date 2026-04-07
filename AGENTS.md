# AGENTS.md - Factorio Mod Template Repository Rules

**简体中文** | [English](AGENTS.en.md)

本文件定义 `factorio-mod-starter-ai` 的仓库级默认约束。这是一个**指导性模板仓库**，用于帮助开发者通过 AI 辅助完成 Factorio 模组开发与自动发布。

## Repository Purpose

这是一个 **Factorio 模组开发模板仓库**，提供：

- 完整的多模组工作区结构
- 自动打包和发布系统
- AI 协作规范和边界规则
- 开发指南和最佳实践文档

**这不是一个具体的模组项目**，而是一个可复制的起点模板。

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

## Workspace Hygiene

- 不要把 zip、日志、截图、临时脚本直接堆在仓库根目录
- 产物与调试文件优先放到 `artifacts/` 或 `dist/`
- 本地缓存目录如 `.local/`、`.sisyphus/`、`.codex/` 不应成为正式产物的一部分
- 打包输出默认在 `/home/factorio-mod-zips/`，CI 环境使用 `dist/`

## Before Finishing Work

完成修改前，默认应检查：

1. `info.json` 字段是否完整且合法（必需字段：name, version, factorio_version, title, author, description）
2. 目录是否仍符合 `<mod>/src/` 结构
3. 是否至少有一个入口文件（`control`/`data`/`settings`）
4. `python3 pack_mods.py` 是否仍可成功打包模组
5. 是否遵循了 Factorio 阶段边界规则

## Template Usage

使用此模板创建新项目时：

1. 复制整个仓库结构
2. 删除或替换 `example-mod/` 为你的实际模组
3. 配置 GitHub Secret `FACTORIO_TOKEN`
4. 阅读 `docs/` 下的所有文档
5. 遵循 `.github/AI_RULES.md` 中的规范

## Documentation Structure

- `README.md` - 模板概览和快速开始
- `AGENTS.md` - 本文件，仓库边界规则
- `.github/AI_RULES.md` - AI 协作强制规范
- `CONTRIBUTING.md` - 贡献指南
- `docs/SETUP.md` - 环境配置指南
- `docs/MOD_DEVELOPMENT.md` - 模组开发规范
- `docs/PUBLISHING.md` - 发布流程文档
- `docs/TROUBLESHOOTING.md` - 故障排查指南
