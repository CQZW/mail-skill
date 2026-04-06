---
name: mail
description: Use when Claude Code should help with fromaiagent mailboxes, including profile management, signed tool arguments, and project MCP setup.
---

# mail for Claude Code

Use this skill when Claude Code needs to work with fromaiagent mailboxes.

## Workflow

1. Use the shell wrappers in `scripts/` first.
2. Let the wrapper auto-select Python or Node.js.
3. Manage mailbox profiles with `scripts/profile.sh`.
4. Prepare official MCP tool arguments with `scripts/prepare-tool-args.sh`.
5. Add the official MCP server with `claude mcp add --transport http -s project fromaiagent https://api.fromaiagent.com/mcp`, then restart Claude Code before testing.

## Rules

- Prefer saved profiles over asking the developer to re-find private keys.
- Use `scripts/profile.sh create <name> [address]` to create a local mailbox keypair when no profile exists yet.
- After registration succeeds, use `scripts/profile.sh assign-address <profile> <address>` to write the activated mailbox address back into the local profile.
- If multiple profiles exist, confirm the active one before `send_mail` or `rotate_key`.
- Use `scripts/prepare-tool-args.sh` instead of rebuilding signatures manually.
- For `send_mail`, `bodyText` is the preferred field name. If the args file uses `body`, the scripts will map it to `bodyText` before signing.
- Use the shell wrappers first so the skill can adapt to Python or Node.js automatically.
- When using Claude Code, make sure the official MCP server has been added for the project and restart Claude Code if the mailbox tools do not appear.
- For `create_mailbox`, allow the args file to omit `address` when the user wants the server to assign one automatically.
- If `send_mail` fails because the plan quota is exceeded, clearly surface the returned upgrade link.
- If `get_mailbox_status` returns a subscription management link, clearly say it can be used to manage or cancel the subscription.
