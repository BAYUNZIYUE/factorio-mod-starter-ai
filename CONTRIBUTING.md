# 贡献指南

欢迎为本模板仓库贡献！本文档介绍如何使用此模板和贡献改进。

## 使用此模板

### 方法 1: 使用 GitHub 模板功能

1. 访问本仓库页面
2. 点击 "Use this template" 按钮
3. 创建你自己的仓库
4. 克隆到本地开始开发

### 方法 2: 手动复制

```bash
git clone https://github.com/your-username/factorio-mod-template.git my-mod-project
cd my-mod-project
rm -rf .git
git init
git add .
git commit -m "Initial commit from template"
```

## 创建你的第一个模组

### 1. 删除或修改示例模组

```bash
rm -rf example-mod/
```

或者复制示例模组作为起点：

```bash
cp -r example-mod/ my-awesome-mod/
```

### 2. 修改模组信息

编辑 `my-awesome-mod/src/info.json`：

```json
{
  "name": "my-awesome-mod",
  "version": "1.0.0",
  "factorio_version": "2.0",
  "title": "My Awesome Mod",
  "author": "Your Name",
  "description": "An awesome mod that does awesome things"
}
```

### 3. 实现你的功能

根据需要修改：
- `settings.lua` - 模组设置
- `data.lua` - 原型定义
- `control.lua` - 运行时逻辑
- `locale/` - 本地化文本

### 4. 测试打包

```bash
export TARGET_MOD="my-awesome-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### 5. 配置 GitHub

1. 创建 GitHub 仓库
2. 配置 `FACTORIO_TOKEN` Secret
3. 推送代码

### 6. 发布第一个版本

```bash
git tag my-awesome-mod-v1.0.0
git push origin my-awesome-mod-v1.0.0

gh release create my-awesome-mod-v1.0.0 \
  --title "My Awesome Mod v1.0.0" \
  --notes "Initial release"
```

## 贡献到模板仓库

如果你想改进这个模板本身，欢迎提交 Pull Request！

### 贡献类型

- 修复文档错误或不清晰的地方
- 改进示例模组
- 增强打包脚本
- 改进 workflow
- 添加新的文档章节

### 提交 Pull Request

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/improve-docs`
3. 提交更改：`git commit -m "Improve documentation"`
4. 推送到你的 fork：`git push origin feature/improve-docs`
5. 创建 Pull Request

### 代码规范

- Python 代码遵循 PEP 8
- Lua 代码使用 2 空格缩进
- 文档使用 Markdown 格式
- 提交信息使用清晰的描述

## 模组开发最佳实践

### 目录命名

- 使用 kebab-case（小写字母 + 连字符）
- 模组目录名必须与 `info.json` 中的 `name` 一致
- 示例：`my-awesome-mod`

### 版本管理

- 使用语义化版本号：`major.minor.patch`
- 每次发布前更新 `info.json` 和 `changelog.txt`
- Tag 格式：`<mod-name>-v<version>`

### 代码组织

- 保持 `control.lua` 简洁，复杂逻辑放到 `scripts/`
- 使用 `prototypes/` 目录组织原型定义
- 所有玩家可见文本放到 `locale/`

### 测试

- 在游戏中测试所有功能
- 测试与其他流行模组的兼容性
- 测试旧存档加载（如果修改了原型）

### 文档

- 在模组根目录添加 `README.md`
- 说明模组功能、配置选项、已知问题
- 提供截图或视频演示

## 多模组工作区

本模板支持在一个仓库中开发多个模组。

### 添加新模组

1. 在仓库根目录创建新的模组目录
2. 遵循标准目录结构：`<mod-name>/src/info.json`
3. 测试打包：`TARGET_MOD="new-mod" python3 pack_mods.py`

### 选择性发布

使用 tag 格式 `<mod-name>-v<version>` 只发布特定模组：

```bash
git tag mod-a-v1.0.0
git push origin mod-a-v1.0.0
```

只会打包和发布 `mod-a`，不影响其他模组。

### 同时发布多个模组

手动触发 workflow 会打包并发布所有模组：

```bash
gh workflow run publish-to-mod-portal.yml
```

## AI 协作规范

如果你使用 AI 助手开发模组，请遵循 `.github/AI_RULES.md` 中的规范。

### 关键规则

- 不要修改核心命名规范（tag 格式、目录结构）
- 不要修改 API 端点和环境变量名称
- 严格遵守 Factorio 阶段边界规则
- 修改后必须测试打包和发布

### 阶段边界

这是最容易出错的地方：

- `settings.lua`: 只定义设置，不能使用 `game`/`script`
- `data.lua`: 只定义原型，不能使用 `game`/`script`
- `control.lua`: 只处理运行时，不能修改 `data.raw`

违反这些规则会导致运行时错误。

## 故障排查

遇到问题时：

1. 查看 [故障排查指南](docs/TROUBLESHOOTING.md)
2. 检查 GitHub Actions 日志
3. 查看 Factorio 日志文件
4. 在 Issues 中搜索类似问题

## 许可证

本模板使用 MIT 许可证。你可以自由使用、修改和分发。

使用此模板创建的模组可以使用任何许可证。

## 参考资料

- [Factorio Lua API 文档](https://lua-api.factorio.com/)
- [Factorio Mod Portal API](https://wiki.factorio.com/Mod_publish_API)
- [Factorio 模组开发教程](https://wiki.factorio.com/Tutorial:Modding_tutorial)
- [Data Lifecycle](https://lua-api.factorio.com/latest/Data-Lifecycle.html)

## 联系方式

- GitHub Issues: 报告 bug 或请求功能
- GitHub Discussions: 讨论和提问
- Factorio 论坛: 分享你的模组

感谢使用本模板！祝你开发愉快！
