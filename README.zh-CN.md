# mail

[English](README.md) | [简体中文](README.zh-CN.md)

让 AI 拥有自己的邮箱，并通过 MCP 与真实世界通信。

`mail` 是一个面向 Codex、Claude Code 和 Cursor 的开源技能包，用来更方便地接入和使用 [fromaiagent](https://www.fromaiagent.com) 邮箱系统。

它主要解决三类实际问题：

- 把邮箱 profile、公钥、私钥集中保存在本地
- 为官方 fromaiagent MCP 工具生成正确签名参数
- 减少开发者和 AI 反复查阅底层邮箱接入文档的成本

这个技能包以 MCP 为唯一通信方式：

- 直接使用已连接的 fromaiagent MCP tools
- 不要用原始 HTTP、`curl`、自写 `fetch` 或手写 JSON-RPC 处理邮箱请求
- 如果 MCP 没连好，先修复平台 MCP 配置，不要继续尝试其它传输方式

## fromaiagent 邮箱系统能做什么

fromaiagent 邮箱系统不是面向手工操作的普通邮箱，而是面向 AI 工作流设计的邮箱能力层。

结合这个 skill，开发者可以：

- 注册并管理专门给 AI 使用的邮箱
- 向外部邮箱和其它 fromaiagent 邮箱发送邮件
- 在 AI 工具里读取收件箱内容、线程和邮箱活动
- 监听新邮件进入邮箱时的事件
- 查询邮箱状态、用量和账户状态
- 在服务端返回管理链接时直接展示给开发者或 AI

这样这个 skill 不只是一个便捷封装，也是一种更直接的 fromaiagent 邮箱接入方式。

## 包含的技能包

仓库内包含三套独立的 `mail` skill：

- `codex/mail`
- `claude/mail`
- `cursor/mail`

每套技能包都包含：

- `SKILL.md`
- 平台对应的安装文件
- `references/`
- `scripts/`

## 从 GitHub 安装到 Codex

对于 Codex，请从 `codex/mail` 子目录安装这个 skill，而不是直接从仓库根目录安装。

示例：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo CQZW/mail-skill \
  --path codex/mail \
  --name mail
```

安装完成后，重启 Codex。

## 快速对话范例

开发者通常通过“怎么和 AI 说”会更快理解这个 skill，而不是先去看底层命令。

### 范例 1：注册新邮箱

开发者：

```text
Use mail to register a new mailbox.
Guarantor email: your-guarantor@gmail.com
Use a generated mailbox address.
```

示例 AI 回复：

```text
邮箱注册请求已发起。

- profile: primary-mailbox
- registrationId: reg_xxxx_xxxx_xxxx
- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: pending_verification
- guarantorAddress: your-guarantor@gmail.com
- verificationExpiresAt: 2026-04-06T08:44:55.525Z

下一步：把担保邮箱里收到的验证码发给我，我会继续完成 verify_mailbox_registration。
```

开发者提供验证码之后，比较真实的后续回复会像这样：

```text
邮箱已激活成功。

- profile: primary-mailbox
- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: active
- publicKeyFingerprint: fp_xxxx...xxxx

我已经把激活后的邮箱地址回填到了本地 profile。
```

### 范例 2：发送测试邮件

开发者：

```text
Use mail to send a test email from primary-mailbox to partner@example.com.
Subject: mail skill test
Body: This is a test email sent through the mail skill.
```

示例 AI 回复：

```text
测试邮件已成功提交。

- from: agent-a1b2c3d4e5f6@fromaiagent.com
- to: partner@example.com
- subject: mail skill test
- mailId: mail_xxxx_xxxx_xxxx
- threadId: thr_xxxx_xxxx_xxxx
- folder: sent
- deliveryStatus: queued
- createdAt: 2026-04-06T10:21:41.142Z
```

如果邮箱返回了服务端限制响应，比较真实的 AI 回复可以像这样：

```text
这次发送被邮箱限制拦住了。

- error: mail_plan_limit_exceeded
- currentPlan: free
- blockedBy: outbound_external_mail_volume
- currentUsage: 5000
- currentLimit: 5000
- nextPlan: plus

管理链接：
<service-provided-link>
```

### 范例 3：查看邮箱状态

开发者：

```text
Use mail to get mailbox status for primary-mailbox.
```

示例 AI 回复：

```text
邮箱状态如下：

- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: active
- currentPlan: plus
- subscriptionStatus: active
- unreadMailCount: 0
- usagePeriod: 2026-04
- outboundExternalMailVolume: 5000 / 10000
- externalAddressCount: 1 / 200
- internalMailVolume: 0 / 100000

管理链接：
<service-provided-link>
```

### 范例 4：读取最新邮件

开发者：

```text
Use mail to read the latest email in primary-mailbox.
```

示例 AI 回复：

```text
最新邮件如下：

- from: sender@example.com
- to: agent-a1b2c3d4e5f6@fromaiagent.com
- subject: Re: mail skill send_mail test
- folder: inbox
- createdAt: 2026-04-06T08:08:15.728Z

正文：
OK, I received it. Replying here to confirm the mailbox is working.
```

## 运行环境

每套技能包都带有同一组脚本：

- `scripts/profile.sh`
- `scripts/profile.py`
- `scripts/profile.js`
- `scripts/doctor.sh`
- `scripts/doctor.py`
- `scripts/doctor.js`
- `scripts/prepare-tool-args.sh`
- `scripts/prepare-tool-args.py`
- `scripts/prepare-tool-args.js`

优先使用 shell 包装脚本：

```bash
bash scripts/profile.sh
bash scripts/doctor.sh
bash scripts/prepare-tool-args.sh
```

shell 包装脚本会按下面的顺序自动选择运行环境：

1. `python3`
2. `python`
3. `node`

签名逻辑在 Python 环境下依赖 `cryptography`。如果本地有 Python，但没有安装 `cryptography`，`prepare-tool-args.sh` 会自动回退到 Node.js。

## 本地 Profile 存储

邮箱 profile 默认保存在：

```text
~/.fromaiagent/profiles.json
```

如果要改成自定义路径：

```bash
export FROMAIAGENT_PROFILE_STORE_PATH=/custom/path/profiles.json
```

## Profile 命令

创建一个新的本地 profile 和 keypair：

```bash
bash scripts/profile.sh create primary-mailbox
```

创建一个带固定邮箱地址的 profile：

```bash
bash scripts/profile.sh create primary-mailbox primary-mailbox@fromaiagent.com
```

常用 profile 命令：

```bash
bash scripts/profile.sh list
bash scripts/profile.sh show primary-mailbox
bash scripts/profile.sh use primary-mailbox
bash scripts/profile.sh assign-address primary-mailbox primary-mailbox@fromaiagent.com
bash scripts/profile.sh add ./profile.json
bash scripts/profile.sh import ./profiles.json
bash scripts/profile.sh export
bash scripts/profile.sh export primary-mailbox
bash scripts/profile.sh remove primary-mailbox
bash scripts/profile.sh remove primary-mailbox --force
```

说明：

- profile 可以先创建，后完成邮箱注册
- 如果 profile 暂时还没有邮箱地址，也可以先用于 `create_mailbox`，让服务端自动分配地址
- 其它需要签名的邮箱工具通常要求 profile 已经有真实邮箱地址

## Doctor 命令

运行：

```bash
bash scripts/doctor.sh
```

它会检查：

- 当前机器是否有可用运行环境
- profile store 是否存在
- 是否已经选择默认 profile
- 当前 profile 是否包含 `publicKey` 和 `privateKey`

如果当前 profile 还没有地址，`doctor` 会把它当作 warning，而不是直接失败。

## 生成签名参数

先准备一个参数文件：

```json
{
  "to": "partner@example.com",
  "subject": "Project update",
  "bodyText": "Here is the latest status."
}
```

对于 `send_mail`，脚本同时兼容 `body` 字段。如果传入的是 `body`，脚本会在签名前自动转换成 `bodyText`。

然后生成签名后的工具参数：

```bash
bash scripts/prepare-tool-args.sh send_mail ./args.json
```

如果要强制指定某个 profile：

```bash
bash scripts/prepare-tool-args.sh send_mail ./args.json primary-mailbox
```

输出结果中会包含：

- `publicKey`
- `nonce`
- `signature`
- `address`

当目标工具要求地址，或者当前 profile 已经带地址时，输出中会自动包含 `address`。

对于 `create_mailbox`，如果你希望由服务端自动分配邮箱地址，可以在参数文件中省略 `address`。

## 支持的官方工具

脚本覆盖完整的官方 fromaiagent 邮箱工具集合：

- `create_mailbox`
- `verify_mailbox_registration`
- `get_mailbox_status`
- `search_ai_partners`
- `create_mail_attachment_upload`
- `send_mail`
- `list_mails`
- `search_mails`
- `get_mail`
- `delete_mail`
- `restore_mail`
- `list_threads`
- `rotate_key`
- `watch_mailbox`

## 注册流程

最短的邮箱注册流程是：

1. 创建本地 profile 和 keypair
2. 为 `create_mailbox` 生成签名参数
3. 直接调用已连接的 `create_mailbox` MCP tool，并传入这份签名参数
4. 从担保邮箱中读取验证码
5. 为 `verify_mailbox_registration` 生成签名参数
6. 直接调用已连接的 `verify_mailbox_registration` MCP tool，并传入这份签名参数
7. 把激活后的邮箱地址回填到本地 profile

示例：

```bash
bash scripts/profile.sh create primary-mailbox
bash scripts/doctor.sh
bash scripts/prepare-tool-args.sh create_mailbox ./create-mailbox.json primary-mailbox
bash scripts/profile.sh assign-address primary-mailbox <activated-address>
```

## 服务端返回的管理链接

当 `send_mail` 返回服务端限制响应时，面向用户的表现应该是：

- 明确说明请求被邮箱限制拦住了
- 如果服务端返回了管理链接，就直接展示出来

当 `get_mailbox_status` 返回管理地址时，面向用户的表现应该是：

- 明确标注这是邮箱管理入口
- 直接展示返回的链接

## 安装到 Codex

把：

```text
codex/mail/
```

复制到：

```text
~/.codex/skills/mail/
```

为了让项目内行为更稳定，建议再把：

```text
codex/mail/AGENTS.md
```

复制到项目根目录，文件名为：

```text
AGENTS.md
```

安装完成后的目录大致如下：

```text
~/.codex/skills/
  mail/
    SKILL.md
    AGENTS.md
    references/
    scripts/

your-project/
  AGENTS.md
```

## 安装到 Claude Code

把：

```text
claude/mail/
```

复制到：

```text
~/.claude/skills/mail/
```

然后为当前项目添加官方 fromaiagent MCP server：

```bash
claude mcp add --transport http -s project fromaiagent https://api.fromaiagent.com/mcp
```

添加完成后，先重启 Claude Code，再开始测试 skill。实际使用中，Claude 往往要在重启后才会稳定暴露邮箱工具。

安装完成后的目录大致如下：

```text
~/.claude/skills/
  mail/
    SKILL.md
    references/
    scripts/
```

## 安装到 Cursor

先把整个 Cursor 技能包：

```text
cursor/mail/
```

复制到：

```text
your-project/.cursor/mail/
```

然后把：

```text
cursor/mail/mcp.json.example
```

复制为：

```text
your-project/.cursor/mcp.json
```

再把：

```text
cursor/mail/mail.mdc
```

复制为：

```text
your-project/.cursor/rules/mail.mdc
```

最简单的安装方式是：

```bash
mkdir -p your-project/.cursor
cp -R cursor/mail your-project/.cursor/mail
cp cursor/mail/mcp.json.example your-project/.cursor/mcp.json
mkdir -p your-project/.cursor/rules
cp cursor/mail/mail.mdc your-project/.cursor/rules/mail.mdc
```

文件复制完成后，还需要：

1. 打开 Cursor Settings
2. 进入 MCP
3. 找到 `fromaiagent`
4. 把它从 `Disabled` 切换成 `Enabled`

如果 Cursor 没有立刻加载到新配置，请在启用 MCP 之后 reload 当前项目窗口。

安装完成后的目录大致如下：

```text
your-project/
  .cursor/
    mail/
      SKILL.md
      references/
      scripts/
      mcp.json.example
      mail.mdc
    mcp.json
    rules/
      mail.mdc
```

在 Cursor 中的使用方式：

1. 确认 `fromaiagent` MCP server 已经启用
2. 用安装好这些文件的项目打开 Cursor
3. 直接对 Cursor 下指令，例如：
   - `Use mail to register a new mailbox`
   - `Use mail to get mailbox status`
   - `Use mail to send a test email`

规则文件会引导 Cursor 优先使用 `.cursor/mail/scripts/...`，而不是临时重写签名逻辑。

## References

每个平台包里都包含：

- `references/profile-format.md`
- `references/tool-map.md`
- `references/troubleshooting.md`

这些文档的目标是让开发者快速上手，而不必反复翻底层接入细节。
