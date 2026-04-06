---
name: mail
description: Use when Cursor should help with fromaiagent mailboxes, including profile management, signed tool arguments, and project cursor MCP and rule setup.
---

# mail for Cursor

Use this skill when Cursor needs to work with fromaiagent mailboxes.

## Workflow

1. Use the shell wrappers in `scripts/` first.
2. Let the wrapper auto-select Python or Node.js.
3. Manage mailbox profiles with `scripts/profile.sh`.
4. Prepare official MCP tool arguments with `scripts/prepare-tool-args.sh`.
5. Use the `.cursor/mcp.json` and `.cursor/rules/mail.mdc` files in this skill package.
6. In Cursor Settings, enable the `fromaiagent` MCP server if it appears as disabled, then reload the project window if needed.

## Rules

- Prefer saved profiles over asking the developer to re-find private keys.
- Use `scripts/profile.sh create <name> [address]` to create a local mailbox keypair when no profile exists yet.
- After registration succeeds, use `scripts/profile.sh assign-address <profile> <address>` to write the activated mailbox address back into the local profile.
- If multiple profiles exist, confirm the active one before `send_mail` or `rotate_key`.
- Use `scripts/prepare-tool-args.sh` instead of rebuilding signatures manually.
- Use the shell wrappers first so the skill can adapt to Python or Node.js automatically.
- Make sure the `fromaiagent` MCP server is enabled in Cursor before testing mailbox tools.
- For `create_mailbox`, allow the args file to omit `address` when the user wants the server to assign one automatically.
- If `send_mail` fails because the plan quota is exceeded, clearly surface the returned upgrade link.
- If `get_mailbox_status` returns a subscription management link, clearly say it can be used to manage or cancel the subscription.
