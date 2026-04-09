---
name: mail
description: Use when Claude Code should register mailboxes, send or read mail, inspect mailbox state, or manage local fromaiagent mailbox profiles through MCP tools.
---

# mail for Claude Code

Use MCP only.

- Never use raw HTTP, `curl`, custom `fetch`, or handwritten JSON-RPC.
- Use `scripts/profile.sh` only for local profile work.
- Use `scripts/prepare-tool-args.sh` only to prepare signed MCP arguments, then call the MCP tool with that JSON.
- If mailbox tools do not appear, tell the developer to run `claude mcp add --transport http -s project fromaiagent https://api.fromaiagent.com/mcp` and restart Claude Code.

Intent map:

- register mailbox -> `create_mailbox`, then `verify_mailbox_registration`
- mailbox status or usage -> `get_mailbox_status`
- send email -> `send_mail`
- read mail -> `list_mails`, then `get_mail` or `get_mails`
- mark all unread inbox mail as read -> `mark_all_read`
- search mail -> `search_mails`
- list threads -> `list_threads`
- watch mailbox -> `watch_mailbox`
- delete or restore mail -> `delete_mail` / `restore_mail`
- rotate key -> `rotate_key`
- upload attachment -> `create_mail_attachment_upload`

Decision rules:

- Execute from intent by default.
- Ask only when the sender profile is unclear, or when `send_mail`, `delete_mail`, `restore_mail`, or `rotate_key` is ambiguous.
- If multiple profiles exist and the sender is not explicit, ask which profile to use.
- For `send_mail`, `bodyText` is preferred. If the args file uses `body`, the scripts map it automatically.
- `create_mailbox` may omit the mailbox address when the server should assign one.
- After successful registration, run `scripts/profile.sh assign-address <profile> <address>`.
