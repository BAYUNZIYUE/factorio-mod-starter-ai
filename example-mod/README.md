# Example Mod

这是一个示例模组，展示了 Factorio 模组开发的基本结构和最佳实践。

## 功能

- 添加一个简单的物品 "Example Item"
- 新玩家创建时自动获得 10 个示例物品
- 演示正确的 Factorio 阶段边界使用
- 包含设置项示例（启动设置、全局运行时设置、玩家设置）
- 完整的本地化支持

## 文件结构

```
example-mod/
├── README.md
└── src/
    ├── info.json           # 模组元数据
    ├── settings.lua        # 设置定义（Settings 阶段）
    ├── data.lua            # 原型定义（Data 阶段）
    ├── control.lua         # 运行时逻辑（Control 阶段）
    ├── changelog.txt       # 版本更新日志
    └── locale/
        └── en/
            └── locale.cfg  # 英文本地化
```

## 阶段边界说明

### Settings 阶段 (`settings.lua`)
- **只能做**: 定义模组设置
- **禁止**: 使用运行时 API（`game`, `script`）

### Data 阶段 (`data.lua`)
- **只能做**: 定义和修改原型（`data:extend`, `data.raw`）
- **禁止**: 使用运行时 API（`game`, `script`）

### Control 阶段 (`control.lua`)
- **只能做**: 运行时逻辑、事件处理
- **禁止**: 修改原型（`data.raw` 只读）

## 使用方法

1. 复制此目录作为你的新模组起点
2. 修改 `src/info.json` 中的模组信息
3. 根据需要修改或删除示例代码
4. 添加你自己的功能

## 开发提示

- 所有玩家可见的文本都应该在 `locale/` 中定义
- 使用 `data-final-fixes.lua` 来确保你的修改在其他模组之后执行
- 复杂的运行时逻辑应该放在 `scripts/` 目录下，保持 `control.lua` 简洁
- 修改原型标识时，考虑添加 `migrations/` 来保持存档兼容性

## 参考资料

- [Factorio Lua API 文档](https://lua-api.factorio.com/)
- [Data Lifecycle](https://lua-api.factorio.com/latest/Data-Lifecycle.html)
- [模组开发教程](https://wiki.factorio.com/Tutorial:Modding_tutorial)
