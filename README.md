# Factorio Mod Starter AI

**简体中文** | [English](README.en.md)

🤖 **AI 友好的 Factorio 模组开发模板**，支持自动打包和发布到 Mod Portal。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Factorio](https://img.shields.io/badge/Factorio-2.0+-orange.svg)](https://factorio.com)

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
git clone https://github.com/YOUR_USERNAME/factorio-mod-template.git my-factorio-mods
cd my-factorio-mods

# 删除示例模组，开始你的项目
rm -rf example-mod/
```

### 2. 配置 Factorio API Key

1. 访问 https://factorio.com/profile
2. 生成 API Key，勾选 `ModPortal: Publish Mods`
3. 在 GitHub 仓库添加 Secret：`FACTORIO_TOKEN`

详见 [配置指南](docs/SETUP.md)

### 3. 创建你的第一个模组

```bash
# 创建模组目录
mkdir -p my-awesome-mod/src

# 创建 info.json
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

# 创建入口文件
echo "-- My awesome mod" > my-awesome-mod/src/control.lua
```

### 4. 发布到 Mod Portal

```bash
# 创建 release（自动触发发布）
gh release create my-awesome-mod-v1.0.0 \
  --title "My Awesome Mod v1.0.0" \
  --notes "Initial release"
```

---

## 📚 文档导航

### 给开发者

- **[完整设置指南](docs/SETUP.md)** - 从零开始配置开发环境
- **[模组开发规范](docs/MOD_DEVELOPMENT.md)** - 目录结构、命名规则、最佳实践
- **[发布流程](docs/PUBLISHING.md)** - 如何发布单个或多个模组
- **[故障排查](docs/TROUBLESHOOTING.md)** - 常见问题和解决方案

### 给 AI 助手

- **[AI 协作规则](.github/AI_RULES.md)** - 强制性规范，AI 必读
- **[仓库边界文件](AGENTS.md)** - 仓库级约束和规则
- **[工作流说明](.github/workflows/README.md)** - CI/CD 流程说明

---

## 🏗️ 仓库结构

```
factorio-mod-template/
├── .github/
│   ├── workflows/
│   │   └── publish-to-mod-portal.yml    # 自动发布 workflow
│   └── AI_RULES.md                       # AI 强制规范
├── docs/
│   ├── SETUP.md                          # 设置指南
│   ├── MOD_DEVELOPMENT.md                # 开发规范
│   ├── PUBLISHING.md                     # 发布流程
│   └── TROUBLESHOOTING.md                # 故障排查
├── example-mod/                          # 示例模组（可删除）
│   └── src/
│       ├── info.json
│       └── control.lua
├── pack_mods.py                          # 打包脚本
├── AGENTS.md                             # 仓库边界规则
├── CONTRIBUTING.md                       # 贡献指南
├── .gitignore
└── README.md                             # 本文件
```

---

## ✨ 核心特性

### 1. 多模组支持

在同一仓库中管理多个模组，每个模组独立发布：

```bash
# 只发布 mod-a
gh release create mod-a-v1.0.0 --title "Mod A v1.0.0" --notes "..."

# 只发布 mod-b  
gh release create mod-b-v2.1.0 --title "Mod B v2.1.0" --notes "..."
```

### 2. 自动化发布

- 创建 release → 自动打包 → 自动上传到 Mod Portal
- 支持手动触发
- 完整的错误处理和日志

### 3. AI 友好

- 详细的边界文件和规范
- 清晰的目录结构
- 完整的验证命令
- 防止 AI 破坏核心逻辑

### 4. 最佳实践

- 遵循 Factorio 官方规范
- 支持 TypeScript（可选）
- 本地化支持
- 版本管理和 changelog

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
- ✅ API 端点：`init_publish`（不是 `init_upload`）
- ❌ 禁止修改核心环境变量名称
- ❌ 禁止修改 workflow 触发条件

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

- **问题反馈**: [GitHub Issues](https://github.com/YOUR_USERNAME/factorio-mod-template/issues)
- **讨论**: [GitHub Discussions](https://github.com/YOUR_USERNAME/factorio-mod-template/discussions)

---

**开始你的 Factorio 模组开发之旅吧！** 🚂✨
