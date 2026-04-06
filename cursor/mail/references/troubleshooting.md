# troubleshooting

## No profile yet

Create one locally:

```bash
bash scripts/profile.sh create primary-mailbox
```

Or import an existing one:

```bash
bash scripts/profile.sh add ./profile.json
```

## Multiple profiles but no default profile

Select one:

```bash
bash scripts/profile.sh use primary-mailbox
```

## `create_mailbox` still reports `invalid_signature`

Use `bash scripts/prepare-tool-args.sh` and do not rebuild the signature manually. The skill already applies the correct official tool route and MCP signing behavior.

## `send_mail` plan limit exceeded

This is a billing or quota state, not a generic signing failure. Show the returned upgrade link directly.

## `get_mailbox_status` returned a subscription link

Clearly label it as the subscription management or cancellation entry.

## Signature mismatch

Common causes:

- wrong active profile
- mismatched private key and public key
- skipping the provided signing scripts
- using a profile with no mailbox address for a tool other than `create_mailbox`

## Registration succeeded but the local profile still shows `unassigned`

Write the activated mailbox address back into the profile:

```bash
bash scripts/profile.sh assign-address <profile> <activated-address>
```
