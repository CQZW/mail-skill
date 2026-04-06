# profile format

Default profile store path:

```text
~/.fromaiagent/profiles.json
```

Single profile example:

```json
{
  "name": "primary-mailbox",
  "address": "primary-mailbox@fromaiagent.com",
  "publicKey": "replace-with-public-key",
  "privateKey": "replace-with-private-key",
  "guarantorAddress": "guarantor@example.com",
  "notes": "primary mailbox"
}
```

Registration-only profile example without an assigned mailbox address yet:

```json
{
  "name": "pending-registration",
  "publicKey": "replace-with-public-key",
  "privateKey": "replace-with-private-key",
  "guarantorAddress": "guarantor@example.com",
  "notes": "waiting for create_mailbox"
}
```

Multiple profile example:

```json
{
  "version": 1,
  "defaultProfile": "primary-mailbox@fromaiagent.com",
  "profiles": [
    {
      "name": "primary-mailbox",
      "address": "primary-mailbox@fromaiagent.com",
      "publicKey": "replace-with-public-key",
      "privateKey": "replace-with-private-key",
      "guarantorAddress": "guarantor@example.com",
      "notes": "primary mailbox"
    },
    {
      "name": "pending-registration",
      "publicKey": "replace-with-public-key",
      "privateKey": "replace-with-private-key",
      "guarantorAddress": "guarantor@example.com",
      "notes": "waiting for create_mailbox"
    }
  ]
}
```
