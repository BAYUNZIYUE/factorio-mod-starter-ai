# 安全与踩坑总结

**简体中文** | [English](SECURITY_AND_PITFALLS.en.md)

这份文档总结了本模板在搭建、联调和自动发布过程中最容易踩到的坑。最重要的目标只有两个：

1. **不要泄露账号、Token、API Key、发布权限**
2. **不要因为 AI 或自动化误操作，把测试内容发布到不可撤回的平台**

---

## 一、最重要的结论

### 1. Factorio Mod Portal 发布后基本不可撤回

- 已发布模组**不能当作普通测试产物随便发**
- 已发布版本**不能直接删除**
- 错误发布后，通常只能：
  - 上传修复版本
  - 标记旧版本为弃用
  - 联系官方支持尝试处理

这意味着：**不要把“创建 release”当作普通测试动作。**

### 2. `FACTORIO_TOKEN` 是高风险 Secret

只要仓库里配置了真实的 `FACTORIO_TOKEN`，并且 workflow 允许自动发布，那么：

- AI 误创建 release
- 人工误打 tag
- 复制命令时看漏仓库
- 在错误分支上发布

都可能把内容真的发到 Mod Portal。

所以必须把它视为**生产权限**，而不是普通配置项。

### 3. 本地能测的就不要先上云测

先本地验证：

- `info.json` 是否正确
- 目录结构是否正确
- zip 是否能打出来
- tag 命名是否正确

只有在这些都确认没问题后，才进入 release 流程。

---

## 二、账号与 Secret 安全规则

## 1. 永远不要把这些内容提交进仓库

严禁提交以下内容：

- Factorio API Key
- GitHub Personal Access Token
- GitHub Actions 临时凭证截图
- 浏览器 Cookie
- `.env` 文件
- 包含账号邮箱、用户名、真实作者身份的临时草稿
- 带有敏感 header 的 curl 命令原文

尤其要注意以下高风险内容：

- `Authorization: Bearer ...`
- `FACTORIO_TOKEN=...`
- 终端历史中的发布命令
- Actions 日志截图

## 2. Secret 只放 GitHub Secrets，不放文件

正确做法：

- 在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加 `FACTORIO_TOKEN`

错误做法：

- 写进 `README.md`
- 写进 `docs/`
- 写进 shell 脚本
- 写进 `.env` 后再提交
- 写进 AI 提示词示例

## 3. 不要把真实账号信息写死在模板里

模板应使用占位信息，例如：

- `Your Name`
- `your-username`
- `your-repo`
- `your-mod`

不要在模板里留下：

- 真实 GitHub 用户名
- 真实邮箱
- 真实 Factorio 作者名
- 真实仓库 URL（除非明确就是本仓库自己的文档入口）

## 4. 截图、日志、录屏也会泄露信息

常见泄露来源：

- GitHub Actions 页面截图
- 浏览器自动填充的账号名
- 终端历史
- Mod Portal 页面右上角账号信息
- Release 页面中的仓库名和组织信息

如果要分享截图：

- 先打码账号
- 先打码 token/secret 名称旁边的内容
- 先检查地址栏和页面右上角

---

## 三、AI 使用时的特殊风险

## 1. AI 可能把“解释发布流程”误当成“执行发布流程”

这是最危险的坑之一。

当你对 AI 说：

- “帮我看看怎么发布”
- “帮我测试 workflow”
- “帮我检查 release 流程”

有些 AI 代理可能会直接：

- 创建 tag
- 创建 GitHub release
- 推送触发 workflow

**因此必须显式写清楚：**

- “只检查，不要创建 release”
- “只本地打包，不要触发任何远端发布”
- “没有我明确确认，不要 push tag / 不要创建 release”

## 2. 不要在测试阶段给 AI 可用的真实发布权限

推荐策略：

- 开发和调试阶段：**不配置 `FACTORIO_TOKEN`**
- 只在准备正式发布时，再配置真实 Secret
- 如果要验证 workflow，优先用假仓库或不带 Secret 的仓库

这样就算 AI 误触发 release，也不会真的发到 Mod Portal。

## 3. 不要把 Secret 直接贴给 AI

错误示例：

- “这是我的 API Key，你帮我配一下”
- “这是 Bearer Token，你替我测试一下”

正确做法：

- 你自己去 GitHub 设置里填 Secret
- 给 AI 只描述变量名，不提供值

例如只告诉 AI：

- “仓库里已有 `FACTORIO_TOKEN` Secret”

不要告诉它具体内容。

---

## 四、我们这次实际遇到的坑

## 1. Mod Portal 删除预期是错的

一个典型误区是：

- 以为像普通平台一样，发布错了可以删

实际情况不是这样，所以发布动作必须更保守。

**经验总结：把 Mod Portal 发布当成“近似不可回退”的动作。**

## 2. API 端点按用途区分

经官方 wiki 核实，两个端点并存，不是二选一：

- 首次创建新模组：`POST https://mods.factorio.com/api/v2/mods/init_publish`，Token 需要 `ModPortal: Publish Mods`
- 给已存在的模组发新版本：`POST https://mods.factorio.com/api/v2/mods/releases/init_upload`，Token 需要 `ModPortal: Upload Mods`
- 如需修改模组详情：另需 `ModPortal: Edit Mods`

`init_upload` 不是错误端点，但它只适用于已存在的模组，不能用来创建新模组。workflow 会自动判断模组是否已存在，再选择对应端点。

经验总结：**涉及外部 API 时，不要凭记忆写，先核对官方文档。**

## 3. 首次发布与后续自动发布

首次发布新模组时，workflow 会调用 `init_publish` 自动创建模组页面；后续版本则走 `releases/init_upload`。

如果自动创建失败（例如 Token 权限不足或平台限制），可以手动在 Mod Portal 上传第一个版本作为兜底。

经验总结：**首次发布前确认 Token 有 `Publish Mods` 权限；后续版本需要 `Upload Mods` 权限。**

发布 workflow 使用 `environment: mod-portal-production`。**未在仓库 Settings → Environments 中配置 required reviewers 时，该 environment 没有审批保护**：release 一创建就会直接上传。配置后，release 与手动触发都会暂停等待批准。

## 4. 仓库名、作者名、示例信息容易残留真实身份

模板仓库最容易忽略的问题不是代码，而是“元数据残留”：

- README 里的旧仓库名
- `info.json` 里的作者名
- 示例中的真实用户名
- 文档里的旧链接

经验总结：**做模板时，除了代码，还要检查所有文档、示例和说明文字。**

---

## 五、推荐的安全操作流程

## 阶段 1：开发阶段

此阶段建议：

- 不配置 `FACTORIO_TOKEN`
- 不创建 release
- 不推 tag
- 只做本地打包

建议执行：

```bash
export TARGET_MOD="your-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

## 阶段 2：预发布检查

在准备正式发布前，逐项确认：

- `info.json` 中的版本号正确
- `changelog.txt` 已更新（推荐）
- tag 格式正确
- 模组名和目录名一致
- zip 内容正确
- README 和文档里没有泄露真实 token
- 仓库里没有 `.env`、截图、日志等敏感文件

## 阶段 3：首次正式发布

建议：

- 先人工检查仓库与模组页面
- 先确认 Secret 已正确配置
- 先确认这是正式版本而不是测试版本
- 首次发布由 workflow 调用 `init_publish` 自动创建；失败时再手动上传兜底

## 阶段 4：后续自动发布

只有在首次发布已经跑通后，再使用：

- Git tag
- GitHub release
- 自动上传 workflow

---

## 六、提交前自检清单

提交代码前，检查：

- [ ] 没有提交任何 token、cookie、`.env`、密钥截图
- [ ] 没有把真实账号名写进示例文件
- [ ] 没有把测试命令写成真实仓库命令
- [ ] README / docs 中没有过时链接或旧仓库名
- [ ] 没有在测试阶段误配置 `FACTORIO_TOKEN`
- [ ] 没有创建仅用于测试的 release

发布前，再检查：

- [ ] 我知道 Mod Portal 不支持直接删除
- [ ] 这不是测试版本
- [ ] tag 命名符合 `<mod-name>-v<version>`
- [ ] `info.json` 版本与 tag 一致
- [ ] AI 没有被授权自动创建 release

---

## 七、给 AI 的一句话安全提示

如果你正在使用 AI 辅助开发，建议在每次涉及发布前，先明确补一句：

> 只做本地检查和打包，不要创建 tag，不要创建 GitHub release，不要触发任何远端发布；除非我明确授权。

这句话能显著降低误发布风险。

---

## 八、和哪些文档一起看

- `docs/SETUP.md`：环境配置和 Secret 设置
- `docs/PUBLISHING.md`：发布流程和不可删除警告
- `.github/AI_RULES.md`：AI 协作硬规则
- `AGENTS.md`：仓库边界与约束
