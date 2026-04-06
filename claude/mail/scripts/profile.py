#!/usr/bin/env python3

import base64
import json
import os
import secrets
import sys
from pathlib import Path


STORE_PATH = Path(os.environ.get("FROMAIAGENT_PROFILE_STORE_PATH", "") or (Path.home() / ".fromaiagent" / "profiles.json"))


def read_json_file(file_path: str):
    return json.loads(Path(file_path).expanduser().resolve().read_text(encoding="utf-8"))


def empty_store():
    return {"version": 1, "profiles": []}


def normalize_address(value):
    return value.strip().lower() if isinstance(value, str) and value.strip() else ""


def display_address(profile):
    return profile.get("address") or "unassigned"


def profile_identifier(profile):
    return profile.get("address") or profile.get("name")


def normalize_profile(candidate):
    if not candidate or not isinstance(candidate, dict):
        raise RuntimeError("Profile must be a JSON object.")

    name = candidate.get("name").strip() if isinstance(candidate.get("name"), str) else ""
    public_key = candidate.get("publicKey").strip() if isinstance(candidate.get("publicKey"), str) else ""
    private_key = candidate.get("privateKey").strip() if isinstance(candidate.get("privateKey"), str) else ""
    address = normalize_address(candidate.get("address"))

    if not name:
        raise RuntimeError("Profile is missing name.")
    if not public_key:
        raise RuntimeError(f"Profile {name} is missing publicKey.")
    if not private_key:
        raise RuntimeError(f"Profile {name} is missing privateKey.")

    normalized = {
        "name": name,
        "publicKey": public_key,
        "privateKey": private_key,
    }
    if address:
        normalized["address"] = address
    if isinstance(candidate.get("guarantorAddress"), str) and candidate.get("guarantorAddress").strip():
        normalized["guarantorAddress"] = candidate.get("guarantorAddress").strip().lower()
    if isinstance(candidate.get("notes"), str) and candidate.get("notes").strip():
        normalized["notes"] = candidate.get("notes").strip()
    return normalized


def read_store():
    if not STORE_PATH.exists():
        return empty_store()
    raw = STORE_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return empty_store()
    parsed = json.loads(raw)
    return {
        "version": 1,
        "defaultProfile": parsed.get("defaultProfile") if isinstance(parsed.get("defaultProfile"), str) else None,
        "profiles": [normalize_profile(profile) for profile in parsed.get("profiles", [])] if isinstance(parsed.get("profiles"), list) else [],
    }


def write_store(store):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = STORE_PATH.parent / f".profiles.{os.getpid()}.{secrets.token_hex(4)}.tmp"
    temp_path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(STORE_PATH)


def find_profile(store, identifier):
    return next((profile for profile in store["profiles"] if profile.get("name") == identifier or profile.get("address") == identifier), None)


def resolve_default_profile(store):
    if store.get("defaultProfile"):
        current = find_profile(store, store.get("defaultProfile"))
        if current:
            return current
    if len(store["profiles"]) == 1:
        return store["profiles"][0]
    return None


def ensure_no_conflict(store, candidate):
    if any(profile.get("name") == candidate.get("name") for profile in store["profiles"]):
        raise RuntimeError(f"Duplicate profile name: {candidate.get('name')}")
    if candidate.get("address") and any(profile.get("address") == candidate.get("address") for profile in store["profiles"] if profile.get("address")):
        raise RuntimeError(f"Duplicate profile address: {candidate.get('address')}")


def create_generated_profile(name, address=None):
    normalized_name = name.strip() if isinstance(name, str) else ""
    if not normalized_name:
        raise RuntimeError("Missing profile name.")

    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except Exception as error:
        raise RuntimeError(
            "profile create requires the `cryptography` package. Install it with `python3 -m pip install cryptography` or use the Node.js script."
        ) from error

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    profile = {
        "name": normalized_name,
        "publicKey": base64.b64encode(
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        ).decode("utf-8"),
        "privateKey": base64.b64encode(
            private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        ).decode("utf-8"),
    }
    normalized_address = normalize_address(address)
    if normalized_address:
        profile["address"] = normalized_address
    return profile


def list_profiles():
    store = read_store()
    if not store["profiles"]:
        print("No profiles stored.")
        return
    for profile in store["profiles"]:
        marker = "*" if profile_identifier(profile) == store.get("defaultProfile") else " "
        print(f"{marker} {profile.get('name')} <{display_address(profile)}>")


def show_profile(identifier):
    store = read_store()
    profile = find_profile(store, identifier)
    if not profile:
        raise RuntimeError(f"Profile not found: {identifier}")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


def use_profile(identifier):
    store = read_store()
    profile = find_profile(store, identifier)
    if not profile:
        raise RuntimeError(f"Profile not found: {identifier}")
    store["defaultProfile"] = profile_identifier(profile)
    write_store(store)
    print(f"Default profile set to {profile.get('name')} <{display_address(profile)}>")


def add_profile(file_path):
    store = read_store()
    profile = normalize_profile(read_json_file(file_path))
    ensure_no_conflict(store, profile)
    store["profiles"].append(profile)
    if not store.get("defaultProfile"):
        store["defaultProfile"] = profile_identifier(profile)
    write_store(store)
    print(f"Added profile {profile.get('name')} <{display_address(profile)}>")


def create_profile(name, address=None):
    store = read_store()
    profile = create_generated_profile(name, address)
    ensure_no_conflict(store, profile)
    store["profiles"].append(profile)
    if not store.get("defaultProfile"):
        store["defaultProfile"] = profile_identifier(profile)
    write_store(store)
    print(f"Created profile {profile.get('name')} <{display_address(profile)}>")


def import_profiles(file_path):
    store = read_store()
    imported = read_json_file(file_path)
    profiles = [normalize_profile(profile) for profile in imported.get("profiles", [])] if isinstance(imported.get("profiles"), list) else []
    for profile in profiles:
        ensure_no_conflict(store, profile)
        store["profiles"].append(profile)
    if isinstance(imported.get("defaultProfile"), str) and imported.get("defaultProfile").strip():
        store["defaultProfile"] = imported.get("defaultProfile").strip()
    elif not store.get("defaultProfile") and store["profiles"]:
        store["defaultProfile"] = profile_identifier(store["profiles"][0])
    write_store(store)
    print(f"Imported {len(profiles)} profile(s).")


def export_profiles(identifier=None):
    store = read_store()
    if not identifier:
        print(json.dumps(store, indent=2, ensure_ascii=False))
        return
    profile = find_profile(store, identifier)
    if not profile:
        raise RuntimeError(f"Profile not found: {identifier}")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


def remove_profile(identifier, force=False):
    store = read_store()
    profile = find_profile(store, identifier)
    if not profile:
        raise RuntimeError(f"Profile not found: {identifier}")
    active_identifier = profile_identifier(profile)
    if store.get("defaultProfile") == active_identifier and not force:
        raise RuntimeError(f"Cannot remove the default profile without --force: {profile.get('name')}")
    store["profiles"] = [item for item in store["profiles"] if profile_identifier(item) != active_identifier]
    if store.get("defaultProfile") == active_identifier:
        store["defaultProfile"] = profile_identifier(store["profiles"][0]) if store["profiles"] else None
    write_store(store)
    print(f"Removed profile {profile.get('name')} <{display_address(profile)}>")


def assign_address(identifier, address):
    store = read_store()
    profile = find_profile(store, identifier)
    if not profile:
        raise RuntimeError(f"Profile not found: {identifier}")
    normalized_address = normalize_address(address)
    if not normalized_address:
        raise RuntimeError("Missing mailbox address.")
    if any(item is not profile and item.get("address") == normalized_address for item in store["profiles"]):
        raise RuntimeError(f"Duplicate profile address: {normalized_address}")
    profile["address"] = normalized_address
    if not store.get("defaultProfile"):
        store["defaultProfile"] = profile_identifier(profile)
    write_store(store)
    print(f"Assigned address {normalized_address} to {profile.get('name')}.")


def main():
    _, *rest = sys.argv
    if not rest:
      print("Usage: profile.py <list|show|use|add|create|import|export|remove|assign-address> [...]", file=sys.stderr)
      raise SystemExit(1)

    command, *args = rest
    if command == "list":
        list_profiles()
    elif command == "show":
        show_profile(args[0])
    elif command == "use":
        use_profile(args[0])
    elif command == "add":
        add_profile(args[0])
    elif command == "create":
        create_profile(args[0], args[1] if len(args) > 1 else None)
    elif command == "import":
        import_profiles(args[0])
    elif command == "export":
        export_profiles(args[0] if args else None)
    elif command == "remove":
        identifier = next((item for item in args if not item.startswith("--")), None)
        if not identifier:
            raise RuntimeError("Missing profile identifier")
        remove_profile(identifier, "--force" in args)
    elif command == "assign-address":
        if len(args) < 2:
            raise RuntimeError("Usage: profile.py assign-address <profile-name-or-address> <mailbox-address>")
        assign_address(args[0], args[1])
    else:
        print("Usage: profile.py <list|show|use|add|create|import|export|remove|assign-address> [...]", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
