# mail

Use the `mail` Codex skill for fromaiagent mailbox work.

## Rules

- Check local profiles first.
- Use `scripts/profile.sh` and `scripts/prepare-tool-args.sh` instead of rebuilding mailbox keys or signing logic by hand.
- Keep private keys local.
- If `send_mail` hits a plan limit, clearly show the payment link.
- If `get_mailbox_status` returns a subscription management link, clearly explain it is the manage or cancel entry.
