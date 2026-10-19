# Factorio Mod Starter AI

**简体中文** | [English](README.en.md)

🤖 **面向 AI 协作优化的 Factorio 模组开发模板**，内置自动打包、发布流程与安全边界说明。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Factorio](https://img.shields.io/badge/Factorio-2.0-orange.svg)](https://factorio.com)

---

## 🎯 这个仓库是什么？

这是一个 **开箱即用的 Factorio 模组开发模板**，专为以下场景设计：

- ✅ 使用 AI 助手（如 Claude、ChatGPT、Cursor）辅助开发模组
- ✅ 支持多模组在同一仓库中独立开发和发布
- ✅ 自动化打包和发布到 Factorio Mod Portal
- ✅ 包含完整的 AI 协作规范和边界文件

**不是什么：**
- ❌ 不是一个具体的模组项目
- ❌ 不是 Factorio 模组开发教程（请参考官方文档）
- ❌ 不是代码生成器

---

## 🚀 快速开始

### 1. 使用此模板创建你的仓库

点击右上角 "Use this template" 按钮，或：

```bash
# 克隆此模板
git clone https://github.com/YOUR_USERNAME/factorio-mod-starter-ai.git my-factorio-mods
cd my-factorio-mods

# 手动 clone 到自己的新仓库时，建议重新初始化 git 历史
rm -rf .git && git init
```

> 用 GitHub 的 "Use this template" 创建时不需要清 `.git`。

### 2. 创建你的第一个模组

推荐复制示例作为起点（结构已经是正确的）：

```bash
cp -r example-mod my-awesome-mod
```

然后编辑 `my-awesome-mod/src/info.json`，**必须把 `name` 改成目录名**，并修改
`author`、`description`、`title`。改完后删除原示例：

```bash
rm -rf example-mod
```

也可以从空目录开始：

```bash
mkdir -p my-awesome-mod/src
cat > my-awesome-mod/src/info.json << 'EOF'
{
  "name": "my-awesome-mod",
  "version": "1.0.0",
  "title": "My Awesome Mod",
  "author": "YourName",
  "description": "An awesome Factorio mod",
  "factorio_version": "2.0",
  "dependencies": ["base >= 2.0"]
}
EOF
echo "-- My awesome mod" > my-awesome-mod/src/control.lua
```

`info.json` 与至少一个 `.lua` 入口（`control.lua` / `data.lua` / `settings.lua`）是必需的；
`locale/` 与 `changelog.txt` 按需添加。

### 3. 本地验证与打包

```bash
# 1) 校验源码
python3 verify_mod.py --target my-awesome-mod

# 2) 打包到 dist/
TARGET_MOD="my-awesome-mod" MOD_OUTPUT_DIR=dist python3 pack_mods.py

# 3) 校验 zip 结构（必须在打包之后）
python3 verify_mod.py --zip-dir dist --target my-awesome-mod
```

`dist/` 下应生成 `<name>_<version>.zip`。zip 内部的 `name_version/` 根目录是模板强制约定（`verify_mod.py --zip-dir` 会校验）；官方只强制 zip 文件名格式 `{name}_{version}.zip`。本地开发阶段到这里即可，不需要配置 `FACTORIO_TOKEN`。

`factorio_version` 只能写一个主版本（如 `"2.0"`）。当前 stable 为 2.0.x，2.1 仍为 experimental；2.0 的模组不会自动在 2.1 加载。

详见 [配置指南](docs/SETUP.md)

---

## 🔐 首次正式发布前

1. 访问 https://factorio.com/profile
2. 生成 API Key，按用途勾选权限：
   - `ModPortal: Publish Mods`（首次创建新模组）
   - `ModPortal: Upload Mods`（给已存在的模组发布新版本）
   - `ModPortal: Edit Mods`（如需修改模组详情）
3. 在 GitHub 仓库添加 Secret：`FACTORIO_TOKEN`

> ⚠️ **配置真实 `FACTORIO_TOKEN` 后，创建 release 就会真实发布到 Mod Portal，且已发布版本不可删除。** 开发阶段不要配置该 Secret，本地验证即可。

---

## 🚀 发布到 Mod Portal

> ⚠️ **这会真实发布到 Mod Portal，版本不可删除。** 发布前请确认模组名、版本号与内容均正确，并已通过 `python3 verify_mod.py --target <mod-name> --tag <tag>` 校验。Tag 中的版本必须与 `info.json` 的 `version` 一致。

```bash
# 创建并推送 tag（格式：<mod-name>-v<version>）
git tag my-awesome-mod-v1.0.0
git push origin my-awesome-mod-v1.0.0

# 创建 release（自动触发发布）
gh release create my-awesome-mod-v1.0.0 \
  --title "My Awesome Mod v1.0.0" \
  --notes "Initial release"
```

Workflow 会自动判断 Mod Portal 上是否已存在该模组：不存在时走 `init_publish` 创建，已存在时走 `releases/init_upload` 发布新版本。

手动触发（不创建 release）时必须指定 `target_mod`；上传时还需 `version`（与 `info.json` 一致）与 `confirm=PUBLISH`。`confirm` 留空只打包：`publish` job 不运行、不查询 Portal、不需要 token。

---

## ⚠️ 重要警告

**Factorio Mod Portal 不支持删除已发布内容：**

- ❌ 已发布的模组无法删除
- ❌ 已发布的版本无法删除
- ❌ 发布无法撤回

**使用 AI 辅助开发时：**

- ⚠️ AI 可能误触发 release
- ⚠️ 测试阶段不要配置 `FACTORIO_TOKEN`
- ⚠️ 首次正式发布前人工核对模组名、版本与内容
- ⚠️ 测试期间明确告诉 AI“不要创建 release”

详见 [发布流程](docs/PUBLISHING.md) 中的警告与安全实践。

---

## 📚 文档导航

### 给开发者

- **[完整设置指南](docs/SETUP.md)** - 从零开始配置开发环境
- **[模组开发规范](docs/MOD_DEVELOPMENT.md)** - 目录结构、命名规则、最佳实践
- **[发布流程](docs/PUBLISHING.md)** - 如何发布单个或多个模组
- **[安全与踩坑总结](docs/SECURITY_AND_PITFALLS.md)** - 账号、API、Secrets、防泄露与误发布风险
- **[故障排查](docs/TROUBLESHOOTING.md)** - 常见问题和解决方案

### 给 AI 助手

- **[AI 协作规则](.github/AI_RULES.md)** - 强制性规范，AI 必读
- **[仓库边界文件](AGENTS.md)** - 仓库级约束和规则
- **[工作流说明](.github/workflows/README.md)** - CI/CD 流程说明

---

## 🏗️ 仓库结构

```
factorio-mod-starter-ai/
├── .github/
│   ├── workflows/
│   │   ├── verify.yml                   # push/PR 校验与打包
│   │   └── publish-to-mod-portal.yml    # 发布 workflow
│   └── AI_RULES.md                      # AI 强制规范
├── docs/                                # 中文文档（英文版为 *.en.md）
├── example-mod/                         # 示例模组（可删除）
│   └── src/
├── scripts/
│   └── publish_mod.py                   # Mod Portal 发布脚本
├── mod_utils.py                         # 校验与打包共享逻辑
├── verify_mod.py                        # 校验入口
├── pack_mods.py                         # 打包入口
├── AGENTS.md                            # 仓库规则入口
├── CONTRIBUTING.md                      # 贡献指南
├── .gitignore
└── README.md                            # 本文件
```

---

## ✨ 核心特性

### 1. 多模组支持

在同一仓库中管理多个模组。一个 release 只发布一个模组，且版本不可删除：

```bash
# 只发布 mod-a（会真实发布，请先本地 verify）
gh release create mod-a-v1.0.0 --title "Mod A v1.0.0" --notes "..."

# 只发布 mod-b
gh release create mod-b-v2.1.0 --title "Mod B v2.1.0" --notes "..."
```

### 2. 自动化发布

- 创建 release → 校验 tag/版本 → 打包 → 上传到 Mod Portal
- 首次发布自动走 `init_publish`，后续版本自动走 `releases/init_upload`
- 手动触发默认 dry-run，输入 `confirm=PUBLISH` 才真正上传

### 3. AI 友好

- 详细的边界文件和规范
- 清晰的目录结构
- 完整的验证命令
- 防止 AI 破坏核心逻辑

### 4. 最佳实践

- 遵循 Factorio 官方规范
- 以 `.lua` 为入口文件（Factorio 只加载 `.lua`；如使用 TypeScript，需先用 TypeScriptToLua 编译，模板不内置该编译链）
- 本地化支持
- 版本管理（`changelog.txt` 推荐但非必需）

---

## 🤖 AI 辅助开发

本模板专为 AI 辅助开发优化：

### 推荐的 AI 工作流

1. **让 AI 阅读规范**
   ```
   请阅读 .github/AI_RULES.md 和 AGENTS.md
   ```

2. **创建新模组**
   ```
   请按照 docs/MOD_DEVELOPMENT.md 创建一个新模组
   ```

3. **实现功能**
   ```
   请实现 [具体功能]，遵循 Factorio 的 data/control 阶段边界
   ```

4. **发布模组**
   ```
   请按照 docs/PUBLISHING.md 准备发布 v1.0.0
   ```

### AI 必须遵守的规则

- ✅ Tag 格式：`<mod-name>-v<version>`
- ✅ 目录结构：`<mod-name>/src/info.json`
- ✅ API 端点：首次创建模组用 `init_publish`，已存在的模组发新版本用 `releases/init_upload`（workflow 自动判断，两者都是合法端点）
- ❌ 未获授权不创建 release、不推 tag（发布不可逆）
- ❌ 不把真实 `FACTORIO_TOKEN` 写入仓库，也不要用它“测试发布”
- ❌ 不发布 `example-mod`（workflow 会拒绝）
- ❌ 不修改 `TARGET_MOD`、`MOD_OUTPUT_DIR`、`FACTORIO_TOKEN` 的名称

详见 [AI_RULES.md](.github/AI_RULES.md)

---

## 📖 学习资源

### Factorio 官方文档

- [Lua API 文档](https://lua-api.factorio.com/)
- [Mod Portal API](https://wiki.factorio.com/Mod_publish_API)
- [模组开发教程](https://wiki.factorio.com/Tutorial:Modding_tutorial)

### 社区资源

- [Factorio 论坛 - Modding](https://forums.factorio.com/viewforum.php?f=25)
- [Factorio Discord](https://discord.gg/factorio)
- [Reddit r/factorio](https://www.reddit.com/r/factorio/)

---

## 🤝 贡献

欢迎改进此模板！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)

### 改进建议

- 添加更多示例模组
- 改进文档
- 添加测试框架集成
- 支持更多 CI/CD 平台

---

## 📄 许可证

本模板采用 MIT 许可证。你可以自由使用、修改和分发。

使用此模板创建的模组项目可以使用任何许可证。

---

## 🙏 致谢

- Factorio 开发团队提供的优秀游戏和 API
- 社区贡献的模组开发经验
- AI 辅助开发工具的进步

---

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/YOUR_USERNAME/factorio-mod-starter-ai/issues)
- **讨论**: [GitHub Discussions](https://github.com/YOUR_USERNAME/factorio-mod-starter-ai/discussions)

---

**开始你的 Factorio 模组开发之旅吧！** 🚂✨
