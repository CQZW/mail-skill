# mail

[English](README.md) | [简体中文](README.zh-CN.md)

`mail` is an open-source skill package for working with the [fromaiagent](https://www.fromaiagent.com) mailbox system from Codex, Claude Code, and Cursor.

It is designed to make mailbox operations easier for both developers and AI agents:

- keep mailbox profiles, public keys, and private keys in one local store
- prepare correctly signed arguments for official fromaiagent MCP tools
- reduce the need to repeatedly read low-level mailbox integration documentation

## Packages

This repository includes three separate `mail` skill packages:

- `codex/mail`
- `claude/mail`
- `cursor/mail`

Each package includes:

- `SKILL.md`
- platform-specific setup files
- `references/`
- `scripts/`

## Quick AI Examples

Developers usually understand this skill faster through conversation examples than through raw commands.

### Example 1: Register a New Mailbox

Developer:

```text
Use mail to register a new mailbox.
Guarantor email: your-guarantor@gmail.com
Use a generated mailbox address.
```

Example AI reply:

```text
Mailbox registration started.

- profile: primary-mailbox
- registrationId: reg_xxxx_xxxx_xxxx
- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: pending_verification
- guarantorAddress: your-guarantor@gmail.com
- verificationExpiresAt: 2026-04-06T08:44:55.525Z

Next step: send me the verification code from the guarantor mailbox and I will complete verify_mailbox_registration.
```

After the developer provides the code, a realistic follow-up reply looks like:

```text
Mailbox activated successfully.

- profile: primary-mailbox
- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: active
- publicKeyFingerprint: fp_xxxx...xxxx

I have also written the activated mailbox address back into the local profile.
```

### Example 2: Send a Test Email

Developer:

```text
Use mail to send a test email from primary-mailbox to partner@example.com.
Subject: mail skill test
Body: This is a test email sent through the mail skill.
```

Example AI reply:

```text
Test email submitted successfully.

- from: agent-a1b2c3d4e5f6@fromaiagent.com
- to: partner@example.com
- subject: mail skill test
- mailId: mail_xxxx_xxxx_xxxx
- threadId: thr_xxxx_xxxx_xxxx
- folder: sent
- deliveryStatus: queued
- createdAt: 2026-04-06T10:21:41.142Z
```

If the mailbox hits a plan limit, a realistic AI reply should look like:

```text
The send request was blocked by mailbox plan limits.

- error: mail_plan_limit_exceeded
- currentPlan: free
- blockedBy: outbound_external_mail_volume
- currentUsage: 5000
- currentLimit: 5000
- nextPlan: plus

Upgrade link:
https://api.fromaiagent.com/upgrade?address=<mailbox-address>&targetPlan=<plan>
```

### Example 3: Get Mailbox Status

Developer:

```text
Use mail to get mailbox status for primary-mailbox.
```

Example AI reply:

```text
Mailbox status:

- address: agent-a1b2c3d4e5f6@fromaiagent.com
- status: active
- currentPlan: plus
- subscriptionStatus: active
- unreadMailCount: 0
- usagePeriod: 2026-04
- outboundExternalMailVolume: 5000 / 10000
- externalAddressCount: 1 / 200
- internalMailVolume: 0 / 100000

Manage subscription:
https://api.fromaiagent.com/billing/manage?address=<mailbox-address>&token=<signed-token>
```

### Example 4: Read the Latest Email

Developer:

```text
Use mail to read the latest email in primary-mailbox.
```

Example AI reply:

```text
Latest email:

- from: sender@example.com
- to: agent-a1b2c3d4e5f6@fromaiagent.com
- subject: Re: mail skill send_mail test
- folder: inbox
- createdAt: 2026-04-06T08:08:15.728Z

Body:
OK, I received it. Replying here to confirm the mailbox is working.
```

## Runtime Support

Every package ships with the same script set:

- `scripts/profile.sh`
- `scripts/profile.py`
- `scripts/profile.js`
- `scripts/doctor.sh`
- `scripts/doctor.py`
- `scripts/doctor.js`
- `scripts/prepare-tool-args.sh`
- `scripts/prepare-tool-args.py`
- `scripts/prepare-tool-args.js`

Use the shell wrappers first:

```bash
bash scripts/profile.sh
bash scripts/doctor.sh
bash scripts/prepare-tool-args.sh
```

The shell wrappers choose a runtime in this order:

1. `python3`
2. `python`
3. `node`

For signing, the Python path requires the `cryptography` package. If Python is available but `cryptography` is missing, `prepare-tool-args.sh` falls back to Node.js automatically.

## Local Profile Store

Mailbox profiles are stored locally at:

```text
~/.fromaiagent/profiles.json
```

To use a different store path:

```bash
export FROMAIAGENT_PROFILE_STORE_PATH=/custom/path/profiles.json
```

## Profile Commands

Create a new local profile and keypair:

```bash
bash scripts/profile.sh create primary-mailbox
```

Create a profile with a fixed mailbox address:

```bash
bash scripts/profile.sh create primary-mailbox primary-mailbox@fromaiagent.com
```

Common profile commands:

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

Notes:

- A profile can exist before mailbox registration is complete.
- If a profile has no address yet, it can still be used for `create_mailbox` when you want the server to assign an address automatically.
- Other signed mailbox tools require a real mailbox address.

## Doctor Command

Run:

```bash
bash scripts/doctor.sh
```

It checks:

- whether a supported runtime is available
- whether the profile store exists
- whether a default profile is selected when needed
- whether the active profile includes `publicKey` and `privateKey`

If the active profile has no address yet, `doctor` reports that as a warning instead of a failure.

## Prepare Signed Tool Arguments

Create an args file:

```json
{
  "to": "partner@example.com",
  "subject": "Project update",
  "bodyText": "Here is the latest status."
}
```

For `send_mail`, the scripts also accept `body` as a compatibility alias and convert it to `bodyText` before signing.

Then prepare signed arguments:

```bash
bash scripts/prepare-tool-args.sh send_mail ./args.json
```

To force a specific profile:

```bash
bash scripts/prepare-tool-args.sh send_mail ./args.json primary-mailbox
```

The output includes:

- `publicKey`
- `nonce`
- `signature`
- `address` when the target tool requires one or when the active profile already has one

For `create_mailbox`, you can omit `address` from the args file if you want fromaiagent to assign a mailbox address automatically.

## Supported Official Tools

The scripts support the full official fromaiagent mailbox tool set:

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

## Registration Flow

The shortest mailbox registration flow is:

1. Create a local profile and keypair.
2. Prepare signed arguments for `create_mailbox`.
3. Submit the prepared JSON through your MCP client.
4. Read the verification code from the guarantor mailbox.
5. Prepare signed arguments for `verify_mailbox_registration`.
6. Submit the verification call.
7. Assign the activated mailbox address back to the local profile.

Example:

```bash
bash scripts/profile.sh create primary-mailbox
bash scripts/doctor.sh
bash scripts/prepare-tool-args.sh create_mailbox ./create-mailbox.json primary-mailbox
bash scripts/profile.sh assign-address primary-mailbox <activated-address>
```

## Billing and Subscription Behavior

When `send_mail` fails because the mailbox plan quota is exceeded, the user-facing workflow should:

- clearly say this is a billing or quota issue
- show the returned payment or upgrade link directly

When `get_mailbox_status` returns a subscription management URL, the user-facing workflow should:

- clearly label it as the subscription management entry
- make it clear the same link can be used to manage or cancel the subscription when applicable

## Install for Codex

Copy:

```text
codex/mail/
```

to:

```text
~/.codex/skills/mail/
```

For more reliable project behavior, also copy:

```text
codex/mail/AGENTS.md
```

to your project root as:

```text
AGENTS.md
```

Expected layout:

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

## Install for Claude Code

Copy:

```text
claude/mail/
```

to:

```text
~/.claude/skills/mail/
```

Then add the official fromaiagent MCP server for the current project:

```bash
claude mcp add --transport http -s project fromaiagent https://api.fromaiagent.com/mcp
```

After adding the server, restart Claude Code before testing the skill. Claude often does not expose mailbox tools reliably until it has been restarted.

Expected layout:

```text
~/.claude/skills/
  mail/
    SKILL.md
    references/
    scripts/
```

## Install for Cursor

Copy the entire Cursor package:

```text
cursor/mail/
```

to:

```text
your-project/.cursor/mail/
```

Then copy:

```text
cursor/mail/mcp.json.example
```

to:

```text
your-project/.cursor/mcp.json
```

and copy:

```text
cursor/mail/mail.mdc
```

to:

```text
your-project/.cursor/rules/mail.mdc
```

The easiest setup is:

```bash
mkdir -p your-project/.cursor
cp -R cursor/mail your-project/.cursor/mail
cp cursor/mail/mcp.json.example your-project/.cursor/mcp.json
mkdir -p your-project/.cursor/rules
cp cursor/mail/mail.mdc your-project/.cursor/rules/mail.mdc
```

After the files are in place:

1. Open Cursor Settings.
2. Go to MCP.
3. Find the `fromaiagent` server.
4. Switch it from `Disabled` to `Enabled`.

If Cursor does not pick up the new config immediately, reload the project window after enabling the MCP server.

Expected layout:

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

How to use it in Cursor:

1. Make sure the `fromaiagent` MCP server is enabled.
2. Open the project after the files above are in place.
3. Ask Cursor directly, for example:
   - `Use mail to register a new mailbox`
   - `Use mail to get mailbox status`
   - `Use mail to send a test email`

The rule file will steer Cursor toward `.cursor/mail/scripts/...` instead of rebuilding signatures manually.

## References

Each platform package includes:

- `references/profile-format.md`
- `references/tool-map.md`
- `references/troubleshooting.md`

These files are intended to help developers get started quickly without repeatedly digging through low-level integration details.
