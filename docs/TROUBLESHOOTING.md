# 故障排查指南

**简体中文** | [English](TROUBLESHOOTING.en.md)

本文档列出常见问题和解决方案。

## 打包问题

### 问题 1: 未找到任何模组目录

**错误信息**:
```
未找到任何模组目录（需要存在 <mod>/src/info.json）
```

**原因**: 目录结构不正确

**解决方案**:

1. 确认目录结构：
   ```
   <mod-name>/
   └── src/
       └── info.json
   ```

2. 确认 `info.json` 文件存在且可读

3. 确认模组目录在仓库根目录下

### 问题 2: info.json 缺少字段

**错误信息**:
```
example-mod: info.json 缺少字段: author, description
```

**原因**: `info.json` 缺少必需字段

**解决方案**:

补充所有必需字段：

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

### 问题 3: 缺少入口文件

**错误信息**:
```
example-mod: src/ 中缺少 control/data/settings 入口文件
```

**原因**: `src/` 目录下没有任何入口文件

**解决方案**:

至少创建一个入口文件：
- `control.lua` 或 `control.ts`
- `data.lua` 或 `data.ts`
- `settings.lua` 或 `settings.ts`

## 发布问题

### 问题 1: FACTORIO_TOKEN 未配置

**错误信息**:
```
❌ init_upload failed (HTTP 401)
```

**原因**: GitHub Secret `FACTORIO_TOKEN` 未配置或无效

**解决方案**:

1. 访问 https://factorio.com/profile
2. 生成新的 API Key，勾选 `ModPortal: Publish Mods` 权限
3. 在 GitHub 仓库设置中添加 Secret：
   - Name: `FACTORIO_TOKEN`
   - Value: 你的 API Key

### 问题 2: 模组不存在

**错误信息**:
```
❌ Upload response indicates failure:
{"error": "Mod does not exist"}
```

**原因**: 首次发布新模组时，Mod Portal 上还没有该模组页面

**解决方案**:

首次发布需要手动创建模组页面：

1. 本地打包模组：
   ```bash
   export TARGET_MOD="your-mod"
   export MOD_OUTPUT_DIR="./dist"
   python3 pack_mods.py
   ```

2. 访问 https://mods.factorio.com/
3. 登录并点击 "Upload mod"
4. 填写模组信息并上传 zip 文件
5. 后续版本可以使用自动发布系统

### 问题 3: Tag 格式错误

**错误信息**:
```
发布模组:  (来自 tag: v1.0.0)
错误: 未找到模组 ''
```

**原因**: Tag 格式不符合 `<mod-name>-v<version>` 规范

**解决方案**:

1. 删除错误的 tag：
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

2. 创建正确的 tag：
   ```bash
   git tag example-mod-v1.0.0
   git push origin example-mod-v1.0.0
   ```

### 问题 4: 版本号不一致

**错误信息**:
```
❌ Upload response indicates failure:
{"error": "Version mismatch"}
```

**原因**: Tag 中的版本号与 `info.json` 中的版本号不一致

**解决方案**:

确保两处版本号一致：

- Tag: `example-mod-v1.0.1`
- `info.json`: `"version": "1.0.1"`

### 问题 5: Workflow 使用旧代码

**症状**: 修改了 workflow 文件，但运行时还是使用旧逻辑

**原因**: Workflow 文件修改后未推送到 `main` 分支

**解决方案**:

1. 确认修改已提交并推送：
   ```bash
   git add .github/workflows/publish-to-mod-portal.yml
   git commit -m "Update workflow"
   git push origin main
   ```

2. Release 触发时会使用最新的 `main` 分支代码

3. 如果还是旧代码，尝试手动触发 workflow

## 运行时错误

### 错误 1: attempt to index global 'game' (a nil value)

**原因**: 在 data 阶段使用了运行时 API

**示例**:
```lua
if game.player then
end
```

**解决方案**:

将此逻辑移到 `control.lua`：

```lua
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if player then
  end
end)
```

### 错误 2: data.raw is read-only

**原因**: 在 control 阶段尝试修改原型

**示例**:
```lua
data.raw["item"]["iron-plate"].stack_size = 200
```

**解决方案**:

将此逻辑移到 `data.lua` 或 `data-final-fixes.lua`：

```lua
if data.raw["item"]["iron-plate"] then
  data.raw["item"]["iron-plate"].stack_size = 200
end
```

### 错误 3: attempt to index global 'script' (a nil value)

**原因**: 在 data 阶段使用了 `script` API

**示例**:
```lua
script.on_event(defines.events.on_tick, function() end)
```

**解决方案**:

将事件注册移到 `control.lua`。

### 错误 4: Unknown key "localised_name"

**原因**: 原型类型不支持该字段

**解决方案**:

检查 Factorio API 文档，确认该原型类型支持的字段。

## 本地化问题

### 问题 1: 文本未显示本地化

**症状**: 游戏中显示的是 `item-name.my-item` 而不是实际文本

**原因**: `locale.cfg` 文件格式错误或路径不正确

**解决方案**:

1. 确认文件路径：`src/locale/en/locale.cfg`

2. 确认文件格式：
   ```ini
   [item-name]
   my-item=My Item
   ```

3. 确认没有 BOM 标记（使用 UTF-8 without BOM）

### 问题 2: 中文显示乱码

**原因**: 文件编码不是 UTF-8

**解决方案**:

将 `locale.cfg` 文件保存为 UTF-8 编码（without BOM）。

## 依赖问题

### 问题 1: 模组加载顺序错误

**症状**: 你的模组在依赖模组之前加载

**原因**: 未在 `info.json` 中声明依赖

**解决方案**:

在 `info.json` 中添加依赖：

```json
{
  "dependencies": [
    "base >= 2.0",
    "other-mod >= 1.0"
  ]
}
```

### 问题 2: 可选依赖未检测

**症状**: 代码假设可选依赖存在，但实际未安装

**解决方案**:

在代码中检查可选依赖：

```lua
if mods["optional-mod"] then
end
```

## 性能问题

### 问题 1: 游戏卡顿

**原因**: `on_tick` 事件处理器执行过于频繁

**解决方案**:

使用 `on_nth_tick` 代替：

```lua
script.on_nth_tick(60, function(event)
end)
```

### 问题 2: 存档加载缓慢

**原因**: 全局变量存储了大量数据

**解决方案**:

1. 只存储必要的数据
2. 使用索引而不是存储完整对象
3. 定期清理不再需要的数据

## 兼容性问题

### 问题 1: 旧存档无法加载

**原因**: 修改了原型名称但未提供迁移脚本

**解决方案**:

创建 `migrations/<version>.lua`：

```lua
for _, surface in pairs(game.surfaces) do
  for _, entity in pairs(surface.find_entities_filtered{name = "old-name"}) do
    local position = entity.position
    local force = entity.force
    entity.destroy()
    surface.create_entity{
      name = "new-name",
      position = position,
      force = force
    }
  end
end
```

### 问题 2: 多人游戏不同步

**原因**: 使用了非确定性逻辑（如随机数、时间戳）

**解决方案**:

使用 Factorio 提供的确定性 API：

```lua
local rng = game.create_random_generator()
local value = rng(1, 100)
```

## 调试技巧

### 启用详细日志

在 `control.lua` 中：

```lua
log("Debug: " .. serpent.block(data))
```

日志位置：
- Windows: `%appdata%\Factorio\factorio-current.log`
- Linux: `~/.factorio/factorio-current.log`
- macOS: `~/Library/Application Support/factorio/factorio-current.log`

### 游戏内调试

使用 `/c` 命令执行 Lua 代码：

```
/c game.print("Debug message")
/c game.player.insert({name = "iron-plate", count = 100})
```

### 重新加载模组

修改代码后，使用 `/c game.reload_mods()` 重新加载（仅限 control 阶段代码）。

修改 data 阶段代码需要重启游戏。

## 获取帮助

如果以上方案都无法解决问题：

1. 查看 [Factorio 官方文档](https://lua-api.factorio.com/)
2. 访问 [Factorio 论坛](https://forums.factorio.com/viewforum.php?f=82)
3. 加入 [Factorio Discord](https://discord.gg/factorio)
4. 查看 [GitHub Issues](https://github.com/your-username/your-repo/issues)

提问时请提供：
- 完整的错误信息
- `info.json` 内容
- 相关代码片段
- Factorio 版本
- 模组版本
