# 环境配置指南

**简体中文** | [English](SETUP.en.md)

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

打包所有**非 example** 模组（模板仓库只有 `example-mod` 时会报“未找到任何模组目录”，属预期）：

```bash
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

只想验证示例模组：

```bash
TARGET_MOD="example-mod" MOD_OUTPUT_DIR="./dist" python3 pack_mods.py
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

zip 内部的 `name_version/` 根目录是模板强制约定（`verify_mod.py --zip-dir` 会校验）；官方只强制 zip 文件名格式 `{name}_{version}.zip`。

## 配置 Factorio API Key

在继续之前，建议先阅读：[安全与踩坑总结](SECURITY_AND_PITFALLS.md)。

尤其要注意：

- 不要把真实 `FACTORIO_TOKEN` 提交进仓库
- 测试阶段不要急着配置真实 Secret
- 不要把自动发布当成普通测试动作

### 1. 生成 API Key

1. 访问 https://factorio.com/profile
2. 登录你的 Factorio 账号
3. 滚动到 "API Keys" 部分
4. 点击 "Generate new API key"
5. 勾选权限：
   - ✅ `ModPortal: Publish Mods`（首次创建新模组）
   - ✅ `ModPortal: Upload Mods`（给已存在的模组发布新版本）
   - ✅ `ModPortal: Edit Mods`（如需修改模组详情）
6. 点击 "Create"
7. 复制生成的 API Key（只显示一次，请妥善保存）

> 推荐同一个 key 同时勾选 `Publish Mods` 与 `Upload Mods`，之后无需更换；只勾一个会在另一场景返回 403。`Edit Mods` 只在修改描述/分类时需要。

### 2. 在 GitHub 配置 Secret

1. 访问你的 GitHub 仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 填写：
   - Name: `FACTORIO_TOKEN`
   - Secret: 粘贴你的 API Key
5. 点击 "Add secret"

### 3. 验证配置

**不要用 release/tag 来验证配置。** 本地运行 `python3 pack_mods.py` + `python3 verify_mod.py` 即可完成验证。release 一旦触发就会真实发布，且 Mod Portal 版本不可删除。

```bash
export MOD_NAME=my-mod
python3 verify_mod.py --target "$MOD_NAME"                  # 校验 info.json、入口与目录结构
TARGET_MOD="$MOD_NAME" python3 pack_mods.py                 # 输出到 dist/
python3 verify_mod.py --zip-dir dist --target "$MOD_NAME"   # 校验 zip，必须在打包后运行
```

确认 zip 生成且内容正确后，再为正式发布配置 Secret。

## 环境变量说明

### MOD_OUTPUT_DIR

打包输出目录。

- 默认值：`dist`（仓库根目录下）
- 可按需覆盖，例如 `export MOD_OUTPUT_DIR="./out"`
- CI 固定使用 `dist/`，不读取该变量；该变量只影响本地 `pack_mods.py`

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
❌ init 请求失败 HTTP 401
```

解决方案：

1. 确认已在 GitHub 仓库设置中添加 `FACTORIO_TOKEN` Secret
2. 确认 API Key 已勾选 `ModPortal: Publish Mods` 与 `ModPortal: Upload Mods` 权限
3. 确认 API Key 未过期

### 首次发布失败：模组不存在

错误信息：

```
❌ <name>: 上传失败 HTTP <code>: ...（示意，实际以日志为准）
{"error": "Mod does not exist"}
```

解决方案：

- 首次发布新模组时，workflow 会自动调用 `init_publish` 创建模组页面，无需手动创建。
- 若仍报 `Mod does not exist`，通常说明当前走的是 `releases/init_upload`（仅适用于已存在的模组），或 Token 缺少对应权限（`Publish Mods` / `Upload Mods`）。请检查 Token 权限后重试。
- 作为兜底，也可以在 https://mods.factorio.com/ 手动点击 "Upload mod" 创建页面并上传第一个版本。

## 下一步

- 阅读 [模组开发规范](MOD_DEVELOPMENT.md)
- 阅读 [发布流程文档](PUBLISHING.md)
- 查看 [故障排查指南](TROUBLESHOOTING.md)
