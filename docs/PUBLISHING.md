# 发布流程

**简体中文** | [English](PUBLISHING.en.md)

本文档介绍如何发布模组到 Factorio Mod Portal。

## ⚠️ 重要警告

**在发布到 Factorio Mod Portal 之前，请务必阅读以下警告：**

### Factorio Mod Portal 不支持删除已发布的模组

- ❌ **无法删除模组**：一旦发布到 Mod Portal，模组页面将永久存在
- ❌ **无法删除版本**：已发布的版本无法删除，只能标记为弃用
- ❌ **无法撤回**：即使是测试版本，一旦发布就无法撤回

### 如果误发布了模组

你只有以下有限的选择：

1. **发布更高版本号的修复版本**：旧版本无法删除或覆盖，发布 `1.0.1` 修复 `1.0.0` 的错误
2. **标记为弃用**：在 Mod Portal 页面标记版本为 "deprecated"
3. **联系官方支持**：发邮件到 support@factorio.com 请求删除（不保证成功）

### 使用 AI 辅助开发时的特别注意事项

**本模板专为 AI 辅助开发设计，但自动发布功能有风险：**

- ⚠️ **AI 可能误触发发布**：AI 助手可能在测试时意外创建 release
- ⚠️ **测试时禁用自动发布**：在测试阶段，不要配置 `FACTORIO_TOKEN`
- ⚠️ **使用本地打包测试**：先用 `python3 pack_mods.py` 本地测试
- ⚠️ **首次发布前仔细检查**：确认模组名称、版本号、内容都正确

### 推荐的安全实践

1. **测试阶段不配置 Secret**：
   ```bash
   # 只在本地测试打包
   export TARGET_MOD="your-mod"
   export MOD_OUTPUT_DIR="./dist"
   python3 pack_mods.py
   ```

2. **首次发布先确认权限**：
   - 新模组由 workflow 调用 `init_publish` 自动创建并发布
   - 如自动创建失败，再手动上传第一个版本作为兜底
   - 确认一切正常后再持续使用自动发布

3. **使用测试仓库**：
   - 在测试仓库中验证 workflow
   - 不要在测试仓库配置真实的 `FACTORIO_TOKEN`

4. **明确告知 AI**：
   - 在与 AI 对话时明确说明"不要创建 release"
   - 只在你明确要求时才发布

### 如果已经误发布

1. 立即停止 workflow（如果还在运行）
2. 访问 https://mods.factorio.com/mod/your-mod
3. 将错误版本标记为 "deprecated"
4. 发布新的正确版本
5. 在模组描述中说明情况

---

## 发布前检查清单

- [ ] 更新 `src/info.json` 中的 `version` 字段
- [ ] 更新 `changelog.txt`（推荐，但非必需）
- [ ] 测试模组在游戏中可正常加载
- [ ] 本地验证并打包：`python3 verify_mod.py` + `TARGET_MOD="your-mod" python3 pack_mods.py`
- [ ] 验证 zip 文件结构正确
- [ ] 仅在正式发布时配置 `FACTORIO_TOKEN`（GitHub Secret）

## 单模组发布（推荐）

使用 tag 格式 `<mod-name>-v<version>` 触发自动发布。

### 步骤 1: 更新版本信息

编辑 `src/info.json`：

```json
{
  "name": "your-mod",
  "version": "1.0.1",
  ...
}
```

编辑 `changelog.txt`（推荐，非必需）：

```
---------------------------------------------------------------------------------------------------
Version: 1.0.1
Date: 2026-04-07
  Changes:
    - Fixed bug X
    - Added feature Y
```

### 步骤 2: 提交更改

```bash
git add your-mod/src/info.json
git add your-mod/src/changelog.txt   # 若 changelog 放模组根目录，则为 your-mod/changelog.txt
git commit -m "your-mod: Bump version to 1.0.1"
git push origin main
```

### 步骤 3: 创建 tag 和 release

```bash
# 创建 tag（格式：<mod-name>-v<version>）
git tag your-mod-v1.0.1
git push origin your-mod-v1.0.1

# 创建 release
# ⚠️ 这会真实发布到 Mod Portal，已发布版本不可删除
gh release create your-mod-v1.0.1 \
  --title "Example Mod v1.0.1" \
  --notes "Bug fixes and improvements"
```

### 步骤 4: 验证发布

1. 访问仓库的 "Actions" 标签
2. 查看 "Publish to Factorio Mod Portal" workflow
3. 确认 **`Upload to Mod Portal` job 实际运行并成功**（不是 skipped；dry-run 或 prerelease 时它会跳过，Actions 仍显示绿色）
4. 访问 `https://mods.factorio.com/mod/<mod-name>` 确认新版本号已出现

## 多模组发布

一个 release 只发布一个模组。多个模组时，逐个创建 release：

1. 为每个要发布的模组更新 `info.json`（`changelog.txt` 推荐同步更新）并提交
2. 对每个模组创建 tag 与 release，例如 `mod-a-v1.1.0`、`mod-b-v2.0.0`
3. 每个 release 独立触发 workflow，只发布对应模组
4. 在 Actions 中逐个确认结果

如需先预演（不发布），手动触发并指定模组，`confirm` 留空只打包：

```bash
gh workflow run publish-to-mod-portal.yml -f target_mod=mod-a
```

> 此时 `publish` job 不运行：不查询 Mod Portal、不需要 token、不执行发布脚本；
> zip 仍会作为 GitHub Actions artifact 保留。Actions 绿色不代表已发布。

确认产物无误后，带 `version` 与 `confirm` 上传（`version` 必须与 `info.json` 一致）：

```bash
gh workflow run publish-to-mod-portal.yml \
  -f target_mod=mod-a -f version=1.1.0 -f confirm=PUBLISH
```

## Tag 命名规则

**格式**: `<mod-name>-v<version>`

**示例**:
- ✅ `your-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0` (缺少模组名)
- ❌ `your-mod_v1.0.0` (使用下划线)
- ❌ `your-mod-1.0.0` (缺少 v 前缀)

**重要**:
- `<mod-name>` 必须与模组目录名完全一致
- `<version>` 应与 `info.json` 中的版本一致
- Workflow 会从 tag 名称提取模组名，只打包和发布该模组

## 版本号规范

使用语义化版本号：`major.minor.patch`

- `major`: 不兼容的 API 变更
- `minor`: 向后兼容的功能新增
- `patch`: 向后兼容的问题修正

示例：
- `1.0.0` → `1.0.1`: 修复 bug
- `1.0.1` → `1.1.0`: 添加新功能
- `1.1.0` → `2.0.0`: 破坏性变更

## 首次发布新模组

首次发布新模组不再需要手动创建页面：workflow 会检测 Mod Portal 上是否已存在该模组，不存在时调用 `init_publish` 自动创建并发布第一个版本。

### 步骤 1: 本地验证与打包

```bash
python3 verify_mod.py
export TARGET_MOD="your-new-mod"
python3 pack_mods.py
```

### 步骤 2: 创建 release

确认 Token 已勾选 `ModPortal: Publish Mods`（创建新模组）与 `ModPortal: Upload Mods`（后续版本），然后按正常的 tag/release 流程发布。workflow 会自动走 `init_publish`。

### 步骤 3: 手动兜底（可选）

如果自动创建因权限或平台问题失败，可以在 Mod Portal 手动创建页面：

1. 访问 https://mods.factorio.com/
2. 登录你的账号
3. 点击 "Upload mod"
4. 填写模组信息：
   - Name: 模组名称（与 `info.json` 中的 `name` 一致）
   - Title: 显示标题
   - Summary: 简短描述
   - Category: 选择分类
   - License: 选择许可证
5. 上传 zip 文件
6. 点击 "Submit"

页面创建后，后续版本会走 `releases/init_upload` 自动发布。

## 发布失败处理

### 场景 1: Tag 格式错误

错误信息：

```
发布模组:  (来自 tag: v1.0.0)
错误: 未找到模组 ''
```

解决方案：

1. 删除错误的 tag：
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

2. 创建正确的 tag：
   ```bash
   git tag your-mod-v1.0.0
   git push origin your-mod-v1.0.0
   ```

### 场景 2: 版本号不一致

Workflow 会在打包前运行 `verify_mod.py --tag` 校验；不一致时直接失败，不会进入发布。本地仍建议先运行：

```bash
python3 verify_mod.py --target <mod-name> --tag <tag>
```

该脚本会校验 tag 中的模组名/版本与 `info.json` 是否一致；两者不一致时不要创建 release。

### 场景 3: 模组不存在

错误信息：

```
❌ <name>: 上传失败 HTTP <code>: ...（示意，实际以日志为准）
{"error": "Mod does not exist"}
```

解决方案：

首次发布新模组时，workflow 会自动调用 `init_publish` 创建页面（见上文"首次发布新模组"）。若仍报此错，请检查 Token 权限，或改用手动上传兜底。

### 场景 4: API Key 权限不足（403）

错误信息：

```
❌ init 请求失败 HTTP 403: ...
```

解决方案：

1. 访问 https://factorio.com/profile
2. 重新生成 API Key，勾选 `ModPortal: Publish Mods` 与 `ModPortal: Upload Mods`（如需修改详情再加 `ModPortal: Edit Mods`）
3. 更新 GitHub Secret `FACTORIO_TOKEN`

> 401 表示 Secret 缺失或 token 无效，不是 scope 问题；403 才是 scope 不足。

## 回滚版本

如果发布的版本有严重问题，可以发布新的修复版本。

**注意**: Factorio Mod Portal 不支持删除已发布的版本。

### 步骤 1: 修复问题

修复代码中的问题。

### 步骤 2: 发布修复版本

```bash
# 更新版本号（例如 1.0.1 → 1.0.2）
# 编辑 info.json 和 changelog.txt

git add .
git commit -m "Fix critical bug"
git push origin main

git tag your-mod-v1.0.2
git push origin your-mod-v1.0.2

gh release create your-mod-v1.0.2 \
  --title "Example Mod v1.0.2 (Hotfix)" \
  --notes "Fixed critical bug in v1.0.1"
```

### 步骤 3: 标记旧版本为弃用（可选）

在 Mod Portal 页面上，可以将旧版本标记为 "deprecated"。

## 自动发布系统工作原理

### 触发条件

1. **Release 发布**: 检出 tag 指向的提交，提取模组名并发布单个模组；prerelease 不发布
2. **手动触发**: 只打包 `target_mod` 指定的模组；默认 dry-run，只有 `confirm=PUBLISH` 时上传

### 工作流程

1. **提取模组名**: 从 tag 名称提取（如果是 release 触发）
2. **打包模组**: 运行 `pack_mods.py`
3. **上传到 Mod Portal**：
   - 判断 Mod Portal 上是否已存在该模组
   - 新模组调用 `init_publish` 创建并获取上传 URL
   - 已存在的模组调用 `releases/init_upload` 获取上传 URL
   - 上传 zip 文件
   - 验证上传成功

### 环境变量

- `MOD_OUTPUT_DIR`: 打包输出目录（仅本地生效；CI 固定使用 `dist/`）
- `TARGET_MOD`: 指定要打包的模组（从 tag 提取）
- `FACTORIO_TOKEN`: Factorio API Key（GitHub Secret）

## 下一步

- 阅读 [故障排查指南](TROUBLESHOOTING.md)
- 查看 [Factorio Mod Portal API 文档](https://wiki.factorio.com/Mod_publish_API)
