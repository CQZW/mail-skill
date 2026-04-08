# tool map

Use MCP tools first. Do not use raw HTTP or handwritten JSON-RPC.

Intent routing:

- Register mailbox -> `create_mailbox`, then `verify_mailbox_registration`
- Mailbox status or usage -> `get_mailbox_status`
- Send email -> `send_mail`
- Read latest or specific email -> `list_mails`, then `get_mail`
- Search mail -> `search_mails`
- List threads -> `list_threads`
- Watch mailbox -> `watch_mailbox`
- Delete or restore email -> `delete_mail` or `restore_mail`
- Rotate key -> `rotate_key`
- Upload attachment -> `create_mail_attachment_upload`
- Local profile management -> `scripts/profile.sh`

Local helpers:

- `bash scripts/profile.sh create <name> [address]`
- `bash scripts/profile.sh list`
- `bash scripts/profile.sh use <name-or-address>`
- `bash scripts/profile.sh assign-address <profile> <address>`
- `bash scripts/profile.sh export`
- `bash scripts/doctor.sh`
- `bash scripts/prepare-tool-args.sh <tool-name> <args.json> [profile-name-or-address]`
