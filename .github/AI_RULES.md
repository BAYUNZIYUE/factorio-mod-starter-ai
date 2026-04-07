# AI 协作规则

**本文档为强制性规范，所有 AI 助手必须严格遵守。**

## 核心原则

1. **保持框架稳定性** - 不得破坏现有的发布系统
2. **遵循命名规范** - 所有命名必须符合既定规则
3. **验证后再提交** - 修改后必须验证不会破坏现有功能
4. **文档同步更新** - 修改代码时同步更新相关文档

---

## 🚫 禁止修改的核心规则

### 1. Tag 命名格式

**格式：** `<mod-name>-v<version>`

**示例：**
- ✅ `my-awesome-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0` (缺少模组名)
- ❌ `my-awesome-mod_v1.0.0` (使用下划线)
- ❌ `my-awesome-mod-1.0.0` (缺少 v 前缀)

**原因：** Workflow 依赖此格式提取模组名称。

### 2. 模组目录结构

**必需结构：**
```
<mod-name>/
└── src/
    ├── info.json          # 必需
    └── control.lua        # 至少需要一个入口文件
```

**入口文件（至少一个）：**
- `control.lua` 或 `control.ts`
- `data.lua` 或 `data.ts`
- `settings.lua` 或 `settings.ts`

**禁止：**
- 将 `info.json` 放在模组根目录
- 省略入口文件
- 使用其他目录名代替 `src`

### 3. API 端点

**正确端点：** `https://mods.factorio.com/api/v2/mods/init_publish`

**禁止使用：**
- ❌ `init_upload`
- ❌ `releases/init_upload`
- ❌ 任何 v1 API 端点

**认证格式：** `Authorization: Bearer $FACTORIO_TOKEN`

### 4. 环境变量名称

**已定义的环境变量（不得更改）：**
- `TARGET_MOD` - 指定要打包的模组
- `MOD_OUTPUT_DIR` - 打包输出目录
- `FACTORIO_TOKEN` - Factorio API Key

### 5. Workflow 触发条件

**当前配置：**
```yaml
on:
  release:
    types: [published]
  workflow_dispatch:
```

**禁止：**
- 移除 `workflow_dispatch`（手动触发功能）
- 修改 `release` 触发类型

---

## ✅ 允许修改的内容

### 1. 错误处理逻辑

可以改进 workflow 中的错误处理，例如：
- 添加更详细的错误信息
- 改进失败时的回滚机制
- 增强日志输出

### 2. 打包脚本验证

可以增强 `pack_mods.py` 的验证逻辑：
- 添加更多字段检查
- 改进错误提示
- 增加文件完整性验证

### 3. 文档和注释

随时可以改进：
- README 文档
- 代码注释
- 使用示例

---

## 🎯 Factorio 阶段边界规则

**这是 Factorio 模组开发的核心约束，违反会导致运行时错误。**

### Settings 阶段 (`settings.lua`, `settings-updates.lua`, `settings-final-fixes.lua`)

**只能做：**
- 定义模组设置原型
- 使用 `data:extend` 添加设置

**禁止：**
- 访问运行时 API（`game`, `script`, `defines.events`）
- 修改非设置类原型

**示例：**
```lua
-- ✅ 正确
data:extend({
  {
    type = "bool-setting",
    name = "my-mod-enable-feature",
    setting_type = "startup",
    default_value = true
  }
})

-- ❌ 错误
if game.player then  -- game 在 settings 阶段不存在
  -- ...
end
```

### Data 阶段 (`data.lua`, `data-updates.lua`, `data-final-fixes.lua`)

**只能做：**
- 定义和修改原型（prototypes）
- 使用 `data:extend` 添加原型
- 读写 `data.raw` 表
- 访问设置值（通过 `settings.startup`）

**禁止：**
- 访问运行时 API（`game`, `script`, `remote`）
- 注册事件处理器
- 访问游戏状态

**示例：**
```lua
-- ✅ 正确
data:extend({
  {
    type = "item",
    name = "my-item",
    icon = "__my-mod__/graphics/item.png",
    icon_size = 64,
    stack_size = 100
  }
})

-- ✅ 正确：修改现有原型
data.raw["item"]["iron-plate"].stack_size = 200

-- ❌ 错误
script.on_event(defines.events.on_tick, function()  -- script 在 data 阶段不存在
  -- ...
end)
```

### Control 阶段 (`control.lua`, `scripts/`)

**只能做：**
- 注册事件处理器
- 访问运行时 API（`game`, `script`, `remote`, `rendering`）
- 读取运行时设置（`settings.global`, `settings.player`）
- 操作游戏状态（玩家、实体、表面等）

**禁止：**
- 修改 `data.raw`（原型已锁定）
- 使用 `data:extend`
- 定义新原型

**示例：**
```lua
-- ✅ 正确
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  player.insert({name = "iron-plate", count = 100})
end)

-- ✅ 正确：读取运行时设置
local enabled = settings.global["my-mod-enable-feature"].value

-- ❌ 错误
data.raw["item"]["iron-plate"].stack_size = 200  -- data.raw 在 control 阶段只读
```

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
3. 原型锁定（data.raw 变为只读）
  ↓
4. Control 阶段
   - control.lua 加载
   - 事件处理器注册
  ↓
5. 游戏运行
   - 事件触发
   - 运行时逻辑执行
```

---

## 📋 开发检查清单

### 创建新模组时

- [ ] 目录名使用 kebab-case（小写字母 + 连字符）
- [ ] 创建 `src/info.json` 并填写所有必需字段
- [ ] 至少创建一个入口文件（`control.lua`/`data.lua`/`settings.lua`）
- [ ] 测试打包：`TARGET_MOD="your-mod-name" python3 pack_mods.py`
- [ ] 验证 zip 文件结构正确

### 修改现有模组时

- [ ] 更新 `info.json` 中的 `version` 字段
- [ ] 更新 `changelog.txt`（如果存在）
- [ ] 检查是否违反 Factorio 阶段边界
- [ ] 测试打包成功
- [ ] 验证模组在游戏中可加载

### 发布新版本时

- [ ] 确认 `info.json` 版本号正确
- [ ] 确认 `changelog.txt` 已更新
- [ ] Tag 格式正确：`<mod-name>-v<version>`
- [ ] 模组名与目录名一致
- [ ] 版本号与 `info.json` 一致

---

## 🔍 常见错误和解决方案

### 错误 1：`attempt to index global 'game' (a nil value)` in data stage

**原因：** 在 `data.lua` 中使用了运行时 API

**解决：**
- 将运行时逻辑移到 `control.lua`
- 在 data 阶段只定义原型

### 错误 2：`data.raw is read-only` in control stage

**原因：** 在 `control.lua` 中尝试修改原型

**解决：**
- 将原型修改移到 `data.lua` 或 `data-final-fixes.lua`
- 在 control 阶段只读取原型信息

### 错误 3：Tag 格式错误导致 workflow 失败

**原因：** Tag 不符合 `<mod-name>-v<version>` 格式

**解决：**
- 删除错误的 tag：`git tag -d <tag-name> && git push origin :refs/tags/<tag-name>`
- 创建正确的 tag：`git tag <mod-name>-v<version> && git push origin <mod-name>-v<version>`

### 错误 4：打包失败 - 缺少入口文件

**原因：** `src/` 目录下没有 `control`/`data`/`settings` 文件

**解决：**
- 至少创建一个入口文件
- 确保文件扩展名是 `.lua` 或 `.ts`

---

## 📚 参考资料

- [Factorio Mod Portal API](https://wiki.factorio.com/Mod_publish_API)
- [Factorio Lua API 文档](https://lua-api.factorio.com/)
- [Factorio 模组开发教程](https://wiki.factorio.com/Tutorial:Modding_tutorial)
- [Data Lifecycle 文档](https://lua-api.factorio.com/latest/Data-Lifecycle.html)

---

## 🤖 AI 助手特别注意事项

### 在修改代码前

1. **阅读 AGENTS.md** - 了解仓库边界规则
2. **检查现有模式** - 查看其他模组的实现方式
3. **验证阶段边界** - 确认代码在正确的阶段执行
4. **测试打包** - 修改后立即测试打包

### 在回答问题时

1. **明确阶段** - 说明代码应该放在哪个阶段
2. **提供完整示例** - 包含必要的上下文
3. **指出常见陷阱** - 提醒阶段边界限制
4. **验证建议** - 提供测试方法

### 在创建新功能时

1. **先规划阶段** - 确定哪些代码属于哪个阶段
2. **分离关注点** - settings/data/control 严格分离
3. **考虑兼容性** - 旧存档、多人游戏
4. **添加本地化** - 所有玩家可见文本

---

**记住：这些规则不是建议，而是强制要求。违反这些规则会导致发布系统失败或模组无法正常工作。**
