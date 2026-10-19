# 模组开发规范

**简体中文** | [English](MOD_DEVELOPMENT.en.md)

本文档介绍 Factorio 模组开发的核心概念、目录结构和最佳实践。

## 目录结构

每个模组必须遵循以下结构：

```
<mod-name>/
├── README.md                    # 模组说明文档
└── src/
    ├── info.json                # 必需：模组元数据
    ├── control.lua              # 运行时逻辑
    ├── data.lua                 # 原型定义
    ├── settings.lua             # 设置定义
    ├── data-updates.lua         # 原型修改（可选）
    ├── data-final-fixes.lua     # 最终原型修改（可选）
    ├── settings-updates.lua     # 设置修改（可选）
    ├── settings-final-fixes.lua # 最终设置修改（可选）
    ├── changelog.txt            # 推荐但非必需
    ├── thumbnail.png            # 模组缩略图（可选）
    ├── locale/                  # 本地化文件
    │   ├── en/
    │   │   └── locale.cfg
    │   └── zh-CN/
    │       └── locale.cfg
    ├── graphics/                # 图片资源
    ├── sounds/                  # 音频资源
    ├── prototypes/              # 原型定义（可选，用于组织代码）
    ├── scripts/                 # 运行时脚本（可选，用于组织代码）
    └── migrations/              # 存档迁移脚本（可选）
```

`info.json` 是唯一强制文件，其余入口文件按需添加；`changelog.txt` 推荐但非必需。

Factorio 只加载 `.lua` 入口文件。如使用 TypeScript，必须先用 TypeScriptToLua 编译为 `.lua`；本模板不内置该编译链。

## info.json 必需字段

```json
{
  "name": "mod-name",
  "version": "1.0.0",
  "factorio_version": "2.0",
  "title": "Mod Title",
  "author": "Your Name",
  "description": "Mod description",
  "dependencies": ["base >= 2.0"]
}
```

字段说明：

- `name`: 模组内部标识符，必须与目录名一致，使用 kebab-case
- `version`: 语义化版本号（major.minor.patch）
- `factorio_version`: 目标 Factorio 主版本，只能写一个主版本号（如 `"2.0"`）。当前 stable 为 2.0.x，2.1 仍为 experimental；2.0 的模组不会自动在 2.1 加载
- `title`: 玩家可见的模组名称
- `author`: 作者名称
- `description`: 简短描述
- `dependencies`: 依赖列表（可选）

## Factorio 阶段边界

Factorio 的加载流程不止三个阶段。进入游戏后，Settings 与 Data 阶段先执行，原型锁定后进入 control 阶段；control 阶段内部还有明确的回调顺序。每个阶段可用的 API 不同，**违反阶段边界会导致运行时错误。**

### 阶段执行顺序

```
游戏启动
  ↓
1. Settings 阶段
   - settings.lua
   - settings-updates.lua
   - settings-final-fixes.lua
  ↓
2. Data 阶段
   - data.lua
   - data-updates.lua
   - data-final-fixes.lua
  ↓
3. 原型锁定（原型不能再修改）
  ↓
4. Control 阶段：control.lua 加载
   - 顶层只能使用 script、remote、commands
   - game、rendering 在顶层不可用
  ↓
5. on_init（新存档首次创建时）
  ↓
6. migrations（从旧版本存档升级时）
   - src/migrations/<mod-version>.lua
  ↓
7. on_load（每次存档加载时）
  ↓
8. on_configuration_changed（模组或游戏版本变化时）
  ↓
9. 游戏运行
   - 事件触发
   - 运行时逻辑执行
```

### Settings 阶段

**目的**: 定义模组设置项

**可用 API**:
- `data:extend` (仅用于设置原型)

**禁止使用**:
- `game`, `script`, `remote` (运行时 API)
- 非设置类原型

**示例**:

```lua
data:extend({
  {
    type = "bool-setting",
    name = "my-mod-enable-feature",
    setting_type = "startup",
    default_value = true
  }
})
```

### Data 阶段

**目的**: 定义和修改游戏原型（物品、配方、实体等）

**可用 API**:
- `data:extend` (添加新原型)
- `data.raw` (读写现有原型)
- `settings.startup` (读取启动设置)

**禁止使用**:
- `game`, `script`, `remote`, `rendering` (运行时 API)
- 事件处理器

**示例**:

```lua
data:extend({
  {
    type = "item",
    name = "my-item",
    icon = "__my-mod__/graphics/item.png",
    icon_size = 64,
    stack_size = 100
  }
})

if data.raw["item"]["iron-plate"] then
  data.raw["item"]["iron-plate"].stack_size = 200
end
```

### Control 阶段

**目的**: 运行时逻辑和事件处理

**可用 API**（注意可用位置）:
- 顶层：`script` (事件注册、全局变量)、`remote` (模组间通信)、`commands` (自定义控制台命令)
- 仅回调内（`on_init` / `on_configuration_changed` / 事件回调）：`game` (游戏状态访问)、`rendering` (渲染 API)
- 运行时设置：`settings.global`, `settings.player`

**禁止使用**:
- 在 `control.lua` 顶层使用 `game` 或 `rendering`
- 访问 `data` 全局（`data` 在 control 阶段不可访问，原型已锁定）

顶层只允许 `script`、`remote`、`commands`；需要 `game` 的逻辑必须放进 `on_init`、`on_configuration_changed` 或事件回调。

**示例**:

```lua
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if not player then return end
  
  player.insert({name = "my-item", count = 10})
end)
```

## 常见错误和解决方案

### 错误 1: 在 data 阶段使用 game

```lua
if game.player then
end
```

**错误信息**: `attempt to index global 'game' (a nil value)`

**解决**: 将此逻辑移到 `control.lua`

### 错误 2: 在 control 阶段访问 data

```lua
data.raw["item"]["iron-plate"].stack_size = 200
```

**错误信息**: `attempt to index global 'data' (a nil value)`

**原因**: `data` 全局只在 data 阶段存在。control 阶段访问不到 `data`（不是“只读”），原型已锁定。

**解决**: 将此逻辑移到 `data.lua` 或 `data-final-fixes.lua`

### 错误 3: 在 settings 阶段定义非设置原型

```lua
data:extend({
  {
    type = "item",
    name = "my-item"
  }
})
```

**解决**: 将物品定义移到 `data.lua`

## 文件加载顺序

### Settings 阶段

1. `settings.lua` (所有模组)
2. `settings-updates.lua` (所有模组)
3. `settings-final-fixes.lua` (所有模组)

### Data 阶段

1. `data.lua` (所有模组)
2. `data-updates.lua` (所有模组)
3. `data-final-fixes.lua` (所有模组)

**使用场景**:
- `data.lua`: 定义你自己的原型
- `data-updates.lua`: 修改其他模组的原型
- `data-final-fixes.lua`: 确保你的修改在最后执行

## 本地化

所有玩家可见的文本都应该在 `locale/` 中定义。

### locale.cfg 格式

```ini
[item-name]
my-item=My Item

[item-description]
my-item=A useful item.

[mod-setting-name]
my-mod-enable-feature=Enable Feature

[mod-setting-description]
my-mod-enable-feature=Enable or disable the feature.
```

### 在代码中使用

```lua
data:extend({
  {
    type = "item",
    name = "my-item",
    localised_name = {"item-name.my-item"},
    localised_description = {"item-description.my-item"}
  }
})
```

Factorio 会自动根据玩家语言加载对应的 `locale.cfg`。

## 命名规范

### 模组目录名

- 使用 kebab-case（小写字母 + 连字符）
- 必须与 `info.json` 中的 `name` 字段一致
- 示例: `my-awesome-mod`

### 原型名称

- 使用模组名作为前缀，避免冲突
- 使用连字符分隔
- 示例: `my-mod-item`, `my-mod-recipe`

### 文件名

- Lua 文件使用小写字母和连字符
- 示例: `data.lua`, `data-updates.lua`, `control.lua`

## 依赖管理

### 声明依赖

在 `info.json` 中声明依赖：

```json
{
  "dependencies": [
    "base >= 2.0",
    "? optional-mod >= 1.0",
    "! incompatible-mod",
    "(?) hidden-optional >= 1.0"
  ]
}
```

符号说明：
- 无符号: 必需依赖
- `?`: 可选依赖（如果存在则加载）
- `!`: 不兼容（如果存在则报错）
- `(?)`: 隐藏可选依赖（不显示在模组列表）

### 检查可选依赖

```lua
if mods["optional-mod"] then
end
```

## 性能优化

### 避免频繁的 on_tick

```lua
script.on_nth_tick(60, function(event)
end)
```

### 使用事件过滤器

```lua
script.on_event(defines.events.on_built_entity, function(event)
end, {{filter = "name", name = "my-entity"}})
```

### 缓存查找结果

```lua
local my_item_prototype = game.item_prototypes["my-item"]
```

## 存档兼容性

### 使用 migrations

当修改原型名称时，在 `src/migrations/` 下创建迁移脚本：

```
<mod-name>/
└── src/
    └── migrations/
        └── <mod-version>.lua
```

例如模组从 `1.0.0` 升级到 `1.1.0`，迁移文件为 `src/migrations/1.1.0.lua`。文件名中的版本号是**模组版本号**（`info.json` 的 `version`），不是 Factorio 版本号；Factorio 只会执行版本号高于当前存档所记录模组版本的迁移脚本。

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

### 全局变量初始化

```lua
script.on_init(function()
  global.my_data = {}
end)

script.on_configuration_changed(function(data)
  if data.mod_changes["my-mod"] then
  end
end)
```

## 调试技巧

### 日志输出

```lua
log("Debug message: " .. serpent.block(data))
```

日志位置: `%appdata%\Factorio\factorio-current.log` (Windows)

### 游戏内调试

```lua
game.print("Debug: " .. tostring(value))
```

### 使用 /c 命令

在游戏控制台中执行 Lua 代码：

```
/c game.player.insert({name = "my-item", count = 100})
```

## 下一步

- 阅读 [发布流程文档](PUBLISHING.md)
- 阅读 [故障排查指南](TROUBLESHOOTING.md)
- 查看 [Factorio Lua API 文档](https://lua-api.factorio.com/)
