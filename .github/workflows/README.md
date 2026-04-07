# 工作流说明

**简体中文** | [English](README.en.md)

本目录保存 GitHub Actions 工作流文件，用于打包和发布 Factorio 模组。

## 当前工作流

### `publish-to-mod-portal.yml`

作用：

- 在发布 GitHub Release 时自动打包指定模组
- 在手动触发时打包并发布所有模组
- 将生成的 zip 上传到 Factorio Mod Portal

## 触发方式

### 1. Release 触发

当创建并发布 GitHub Release 时，workflow 会：

1. 从 tag 中提取模组名
2. 调用 `pack_mods.py` 打包该模组
3. 使用 `FACTORIO_TOKEN` 上传到 Mod Portal

要求 tag 格式必须是：

```text
<mod-name>-v<version>
```

### 2. 手动触发

在 GitHub Actions 页面点击 **Run workflow** 时，workflow 会：

1. 打包仓库中所有符合规则的模组
2. 逐个上传到 Mod Portal

## 关键依赖

- `pack_mods.py`
- GitHub Secret: `FACTORIO_TOKEN`
- 正确的模组目录结构：`<mod-name>/src/info.json`

## 风险提醒

- 一旦配置真实 `FACTORIO_TOKEN`，workflow 就具备正式发布能力
- 不要把 workflow 当作普通测试工具
- 测试阶段建议不要配置真实 Secret
- 发布前请先阅读 `docs/PUBLISHING.md` 和 `docs/SECURITY_AND_PITFALLS.md`

## 相关文档

- [发布流程](../../docs/PUBLISHING.md)
- [安全与踩坑总结](../../docs/SECURITY_AND_PITFALLS.md)
- [AI 协作规则](../AI_RULES.md)
