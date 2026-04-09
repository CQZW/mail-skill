#!/usr/bin/env python3

import base64
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except Exception as error:
    print("Python signing requires the `cryptography` package. Install it with `python3 -m pip install cryptography` or use the Node.js script.", file=sys.stderr)
    raise SystemExit(1) from error


store_path = Path(os.environ.get("FROMAIAGENT_PROFILE_STORE_PATH", "") or (Path.home() / ".fromaiagent" / "profiles.json"))
TOOL_PATHS = {
    "create_mailbox": "/register-mailbox",
    "verify_mailbox_registration": "/verify-mailbox-registration",
    "get_mailbox_status": "/mailbox-status",
    "search_ai_partners": "/search-ai-partners",
    "create_mail_attachment_upload": "/create-mail-attachment-upload",
    "send_mail": "/send-mail",
    "list_mails": "/list-mails",
    "search_mails": "/search-mails",
    "get_mail": "/get-mail",
    "get_mails": "/get-mails",
    "mark_all_read": "/mark-all-read",
    "delete_mail": "/delete-mail",
    "restore_mail": "/restore-mail",
    "list_threads": "/list-threads",
    "rotate_key": "/rotate-key",
    "watch_mailbox": "/watch-mailbox",
}
TOOLS_ALLOW_EMPTY_ADDRESS = {"create_mailbox"}


def read_json(file_path: str):
    return json.loads(Path(file_path).expanduser().resolve().read_text(encoding="utf-8"))


def read_store():
    if not store_path.exists():
        raise RuntimeError(f"Profile store not found: {store_path}")
    parsed = json.loads(store_path.read_text(encoding="utf-8"))
    return {
        "defaultProfile": parsed.get("defaultProfile"),
        "profiles": parsed.get("profiles", []) if isinstance(parsed.get("profiles"), list) else [],
    }


def matches_identifier(profile, identifier):
    return bool(identifier) and (profile.get("name") == identifier or profile.get("address") == identifier)


def resolve_default_profile(store):
    if store.get("defaultProfile"):
        current = next((profile for profile in store["profiles"] if matches_identifier(profile, store.get("defaultProfile"))), None)
        if current:
            return current
    if len(store["profiles"]) == 1:
        return store["profiles"][0]
    return None


def pick_profile(identifier=None):
    store = read_store()
    if identifier:
        exact = next((profile for profile in store["profiles"] if matches_identifier(profile, identifier)), None)
        if not exact:
            raise RuntimeError(f"Profile not found: {identifier}")
        return exact
    current = resolve_default_profile(store)
    if current:
        return current
    raise RuntimeError("No active profile selected.")


def canonical(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return "null" if not (float("-inf") < value < float("inf")) else repr(value)
    if isinstance(value, list):
        return "[" + ",".join(canonical(item) for item in value) + "]"
    if isinstance(value, dict):
        entries = []
        for key in sorted(value.keys()):
            if key == "signature":
                continue
            entries.append(f"{json.dumps(key, ensure_ascii=False)}:{canonical(value[key])}")
        return "{" + ",".join(entries) + "}"
    raise RuntimeError(f"Unsupported value type in canonical JSON: {type(value).__name__}")


def to_pem_from_base64_private_key(base64_key):
    body = "\n".join(base64_key[i:i + 64] for i in range(0, len(base64_key), 64))
    return f"-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----\n".encode("utf-8")


def get_tool_route_path(tool_name: str):
    route = TOOL_PATHS.get(tool_name)
    if not route:
        raise RuntimeError(f"Unsupported tool name: {tool_name}")
    return route


def normalize_address(value):
    return value.strip().lower() if isinstance(value, str) and value.strip() else ""


def resolve_address(tool_name: str, args, profile):
    explicit = normalize_address(args.get("address"))
    if explicit:
        return explicit
    profile_address = normalize_address(profile.get("address"))
    if profile_address:
        return profile_address
    if tool_name in TOOLS_ALLOW_EMPTY_ADDRESS:
        return ""
    raise RuntimeError(f"Tool {tool_name} requires an address. Set one in the args file or the active profile.")


def build_unsigned_body(tool_name, args, profile, address):
    body = {
        **args,
        "publicKey": profile["publicKey"],
    }
    if tool_name == "send_mail" and "bodyText" not in body and isinstance(body.get("body"), str):
        body["bodyText"] = body["body"]
    body.pop("body", None)
    if address:
        body["address"] = address
    else:
        body.pop("address", None)
    body.pop("nonce", None)
    body.pop("signature", None)
    return body


def main():
    _, *rest = sys.argv
    if len(rest) < 2:
        print("Usage: prepare-tool-args.py <tool-name> <args.json> [profile-name-or-address]", file=sys.stderr)
        raise SystemExit(1)

    tool_name, args_file, *tail = rest
    profile_identifier = tail[0] if tail else None

    profile = pick_profile(profile_identifier)
    if not profile.get("publicKey") or not profile.get("privateKey"):
        raise RuntimeError("Active profile must include publicKey and privateKey.")

    args = read_json(args_file)
    address = resolve_address(tool_name, args, profile)
    unsigned_body = build_unsigned_body(tool_name, args, profile, address)
    prepared = {
        **unsigned_body,
        "nonce": args["nonce"] if isinstance(args.get("nonce"), str) and args.get("nonce") else secrets.token_urlsafe(18)[:32],
    }

    body = canonical(unsigned_body)
    body_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
    signing_text = "\n".join([
        "FROMAIAGENT-SIGNATURE-V1",
        "POST",
        get_tool_route_path(tool_name),
        address,
        prepared["nonce"],
        body_sha256,
    ]).encode("utf-8")

    pem = to_pem_from_base64_private_key(profile["privateKey"])
    private_key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise RuntimeError("Loaded private key is not an Ed25519 private key.")
    signature = base64.b64encode(private_key.sign(signing_text)).decode("utf-8")

    prepared["signature"] = signature
    print(json.dumps(prepared, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
