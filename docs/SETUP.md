# 环境配置指南

本文档介绍如何配置开发环境和 Factorio API Key，以便使用自动发布系统。

## 前置要求

- Python 3.x
- Git
- GitHub 账号
- Factorio 账号

## 本地开发环境

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. 测试打包脚本

打包单个模组：

```bash
export TARGET_MOD="example-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

打包所有模组：

```bash
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

验证输出：

```bash
ls -lh dist/
# 应该看到: example-mod_1.0.0.zip
```

### 3. 验证 zip 文件结构

```bash
unzip -l dist/example-mod_1.0.0.zip
```

正确的结构应该是：

```
example-mod_1.0.0/
├── info.json
├── control.lua
├── data.lua
├── settings.lua
├── changelog.txt
└── locale/
    └── en/
        └── locale.cfg
```

## 配置 Factorio API Key

### 1. 生成 API Key

1. 访问 https://factorio.com/profile
2. 登录你的 Factorio 账号
3. 滚动到 "API Keys" 部分
4. 点击 "Generate new API key"
5. 勾选权限：
   - ✅ `ModPortal: Publish Mods`
6. 点击 "Create"
7. 复制生成的 API Key（只显示一次，请妥善保存）

### 2. 在 GitHub 配置 Secret

1. 访问你的 GitHub 仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 填写：
   - Name: `FACTORIO_TOKEN`
   - Secret: 粘贴你的 API Key
5. 点击 "Add secret"

### 3. 验证配置

创建一个测试 release 来验证配置：

```bash
# 确保 info.json 中的版本是 1.0.0
git tag example-mod-v1.0.0
git push origin example-mod-v1.0.0

# 创建 release
gh release create example-mod-v1.0.0 \
  --title "Example Mod v1.0.0" \
  --notes "Initial release"
```

检查 GitHub Actions 是否成功运行：

1. 访问仓库的 "Actions" 标签
2. 查看 "Publish to Factorio Mod Portal" workflow
3. 确认所有步骤都成功（绿色勾号）

## 环境变量说明

### MOD_OUTPUT_DIR

打包输出目录。

- 默认值：`/home/factorio-mod-zips`
- CI 环境：`${{ github.workspace }}/dist`
- 本地开发：`./dist`

### TARGET_MOD

指定要打包的模组名称。

- 为空：打包所有模组
- 指定名称：只打包该模组

示例：

```bash
# 只打包 example-mod
export TARGET_MOD="example-mod"
python3 pack_mods.py

# 打包所有模组
unset TARGET_MOD
python3 pack_mods.py
```

### FACTORIO_TOKEN

Factorio API Key，用于上传模组到 Mod Portal。

- 本地测试：不需要（只测试打包）
- CI 环境：必需（GitHub Secret）

## 故障排查

### 打包失败：找不到模组

错误信息：

```
未找到任何模组目录（需要存在 <mod>/src/info.json）
```

解决方案：

1. 确认目录结构正确：`<mod-name>/src/info.json`
2. 确认 `info.json` 文件存在且格式正确
3. 确认至少有一个入口文件（`control.lua`/`data.lua`/`settings.lua`）

### 打包失败：缺少字段

错误信息：

```
example-mod: info.json 缺少字段: author, description
```

解决方案：

在 `info.json` 中补充缺少的字段：

```json
{
  "name": "example-mod",
  "version": "1.0.0",
  "factorio_version": "2.0",
  "title": "Example Mod",
  "author": "Your Name",
  "description": "Mod description"
}
```

### GitHub Actions 失败：FACTORIO_TOKEN 未配置

错误信息：

```
❌ init_upload failed (HTTP 401)
```

解决方案：

1. 确认已在 GitHub 仓库设置中添加 `FACTORIO_TOKEN` Secret
2. 确认 API Key 有 `ModPortal: Publish Mods` 权限
3. 确认 API Key 未过期

### 首次发布失败：模组不存在

错误信息：

```
❌ Upload response indicates failure:
{"error": "Mod does not exist"}
```

解决方案：

首次发布新模组时，需要先在 Mod Portal 手动创建模组页面：

1. 访问 https://mods.factorio.com/
2. 登录你的账号
3. 点击 "Upload mod"
4. 填写模组信息并上传第一个版本
5. 之后可以使用自动发布系统

## 下一步

- 阅读 [模组开发规范](MOD_DEVELOPMENT.md)
- 阅读 [发布流程文档](PUBLISHING.md)
- 查看 [故障排查指南](TROUBLESHOOTING.md)
