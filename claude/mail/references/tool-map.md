# tool map

Official fromaiagent MCP tools:

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
- `rotate_key`
- `watch_mailbox`

Preferred local scripts:

- `scripts/profile.sh`
- `scripts/doctor.sh`
- `scripts/prepare-tool-args.sh`
- `scripts/profile.py`
- `scripts/profile.js`
- `scripts/doctor.py`
- `scripts/doctor.js`
- `scripts/prepare-tool-args.py`
- `scripts/prepare-tool-args.js`

Useful profile commands:

- `bash scripts/profile.sh create <name> [address]`
- `bash scripts/profile.sh list`
- `bash scripts/profile.sh use <name-or-address>`
- `bash scripts/profile.sh assign-address <profile> <address>`
- `bash scripts/profile.sh export`

Useful signing command:

- `bash scripts/prepare-tool-args.sh <tool-name> <args.json> [profile-name-or-address]`
