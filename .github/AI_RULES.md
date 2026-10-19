# AI 协作规则

**简体中文** | [English](AI_RULES.en.md)

本文件是 `AGENTS.md` 的展开，供需要细节的会话按需读取。两者冲突时，以更严格的安全条款为准：**不可逆操作、凭据、发布** 优先。

## 1. 不可修改的契约

### Tag

```text
<mod-name>-v<major.minor.patch>
```

- 版本必须与 `src/info.json` 的 `version` 完全一致
- `mod-name` 必须与目录名、`info.json.name` 一致
- 不要用 `v1.0.0`、`<mod>_v1.0.0`、`<mod>-1.0.0`

### Mod Portal API

| 场景 | 端点 | Token scope |
|---|---|---|
| 首次创建 mod | `POST https://mods.factorio.com/api/v2/mods/init_publish` | `ModPortal: Publish Mods` |
| 已有 mod 发新版本 | `POST https://mods.factorio.com/api/v2/mods/releases/init_upload` | `ModPortal: Upload Mods` |
| 修改描述/分类 | 见官方 Mod details API | `ModPortal: Edit Mods` |

- 认证：`Authorization: Bearer $FACTORIO_TOKEN`
- 两个 init 端点都只接收 `mod`；版本从 zip 内的 `info.json` 读取
- 上传 URL 由 init 响应返回，上传时使用 `multipart/form-data`，字段名 `file`
- 成功响应含 `success: true`；失败含 `error` / `message`
- **没有删除已发布版本的 API**。版本号一旦上传就不可撤回

### 环境变量

- `TARGET_MOD`：只打包指定模组
- `MOD_OUTPUT_DIR`：输出目录，默认 `dist`
- `FACTORIO_TOKEN`：只能放在 GitHub Secrets 或本地环境，禁止入库

### 目录与入口

```text
<mod-name>/src/info.json          # 必需元数据（仍需至少一个 .lua 入口）
<mod-name>/src/control.lua        # 至少一个 .lua 入口
<mod-name>/src/data.lua
<mod-name>/src/settings.lua
```

- `info.json` 必需字段：`name`、`version`、`factorio_version`、`title`、`author`、`description`
- `factorio_version` 只能是两段式主版本（`"2.0"`）；2.0 的 mod 不会在 2.1 自动加载
- 入口只认 `.lua`。TypeScript 必须先用 TypeScriptToLua 编译；模板不内置编译链
- 迁移脚本放 `src/migrations/<mod-version>.lua`；文件名是模组版本，不是 Factorio 版本
- `changelog.txt` 推荐但非必需；若提供，`Version:` 必须存在且与 `info.json` 一致（否则校验失败）；99 个短横线与 `Date:` 缺失只会警告

## 2. 阶段边界

### Settings

允许：`data:extend` 设置原型、`settings.startup`
禁止：`game`、`script`、事件注册、修改非设置原型

### Data

允许：`data:extend`、`data.raw`、原型定义与修改、`settings.startup`
禁止：`game`、`script`、`remote`、事件注册、访问游戏状态

### Control

`control.lua` 顶层：`script`、`remote`、`commands` 用于注册；`settings.global`、`defines`、`log`、`require` 可用。
`game`、`rendering` 在顶层不可用；它们只在 `on_init`、`on_configuration_changed` 和事件回调中可用。
`settings.get_player_settings(player)` 需要 `player` 对象，只能在回调内调用。
`on_load` 只对“之前已属于该存档”的模组执行（新存档 / 新模组不执行）；`storage` 可读不可写；不能访问 `game`；合法用途仅限重建元表、重建条件事件、缓存 `storage` 引用。
`data` 全局在 control 阶段**不存在**（不是“只读”），不能读取也不能修改。

### 加载顺序

```text
settings.lua → settings-updates.lua → settings-final-fixes.lua
data.lua → data-updates.lua → data-final-fixes.lua
control.lua
on_init
migrations（JSON 先，Lua 后）
on_load
on_configuration_changed
事件回调
```

### 示例

```lua
-- ✅ data.lua：只定义原型
data:extend({
  { type = "item", name = "my-item", icon = "__my-mod__/graphics/item.png",
    icon_size = 64, stack_size = 100 }
})

-- ❌ data.lua：运行时 API 不存在
-- script.on_event(defines.events.on_tick, function() end)  -- script is nil
```

```lua
-- ✅ control.lua：顶层只注册
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if player then player.insert({ name = "iron-plate", count = 100 }) end
end)

-- ❌ control.lua 顶层：game 尚未可用
-- game.print("loaded")  -- game is nil at this point
```

## 3. 发布流程

发布是不可逆操作。没有用户明确授权，不要创建 release、不要推 tag、不要调用发布 API。

```bash
# 1. 本地验证
python3 verify_mod.py --target my-mod
TARGET_MOD=my-mod python3 pack_mods.py
python3 verify_mod.py --zip-dir dist --target my-mod

# 2. 打 tag 并创建正式 release（需要授权）
git tag my-mod-v1.0.0
git push origin my-mod-v1.0.0
gh release create my-mod-v1.0.0 --title "My Mod v1.0.0" --notes "..."

# 3. 手动触发（默认 dry-run）
#    target_mod 必填；confirm 输入 PUBLISH 才会上传
```

Workflow 行为：

- release 事件：只发布 tag 指向的提交；prerelease 不发布
- 手动触发：只打包指定模组；`confirm != PUBLISH` 时不上传
- 上传前查询 Mod Portal：mod 不存在走 `init_publish`，存在走 `releases/init_upload`
- 版本已存在时跳过，避免重复发布和重跑失败
- 发布后再次查询 releases，确认版本可见

## 4. 检查清单（命令化）

创建/修改模组：

- [ ] `python3 verify_mod.py --target <mod>`
- [ ] `TARGET_MOD=<mod> python3 pack_mods.py`
- [ ] `python3 verify_mod.py --zip-dir dist --target <mod>`
- [ ] 在游戏中加载验证（至少启动一次，检查日志无 Lua 错误）

发布前：

- [ ] `info.json.version` 已更新
- [ ] `changelog.txt` 顶部版本与 `info.json` 一致
- [ ] tag 版本与 `info.json` 一致
- [ ] 目录名、`info.json.name`、tag 前缀一致
- [ ] 已获得用户明确授权

## 5. 常见错误

| 症状 | 原因 | 处理 |
|---|---|---|
| `attempt to index global 'game' (a nil value)` | data 阶段用了运行时 API | 移到 control.lua 的事件回调 |
| `attempt to index global 'data' (a nil value)` | control 阶段访问 `data` | 原型修改移到 data 阶段 |
| `attempt to index global 'game' (a nil value)` 在 control 顶层 | 顶层读 `game` | 移到 `on_init` 或事件回调 |
| 模组加载后没有入口 | 只有 `.ts`，没有编译出的 `.lua` | 运行 TypeScriptToLua，或改用 `.lua` |
| `ModAlreadyExists` | 对已存在的 mod 调用了 `init_publish` | 改用 `releases/init_upload` |
| 401 | Secret 未配置或 token 无效 | 重新生成并更新 `FACTORIO_TOKEN` |
| 403 | token 有效但 scope 不足 | 首次发布需要 `Publish Mods`，发版需要 `Upload Mods`；推荐同一个 key 同时勾选两者 |
| `Version mismatch` | tag/zip/info.json 版本不一致 | 用 `verify_mod.py --tag` 定位 |
| 打包后 zip 里混入 `.git`/`node_modules` | 旧脚本无排除规则 | 使用当前 `pack_mods.py` |

## 6. 参考资料

- [Mod structure](https://lua-api.factorio.com/latest/auxiliary/mod-structure.html)
- [Data lifecycle](https://lua-api.factorio.com/latest/auxiliary/data-lifecycle.html)
- [Mod publish API](https://wiki.factorio.com/Mod_publish_API)
- [Mod upload API](https://wiki.factorio.com/Mod_upload_API)
- [Lua API](https://lua-api.factorio.com/)
