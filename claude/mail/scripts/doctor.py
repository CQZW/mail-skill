#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path


store_path = Path(os.environ.get("FROMAIAGENT_PROFILE_STORE_PATH", "") or (Path.home() / ".fromaiagent" / "profiles.json"))
issues = []
warnings = []


def matches_identifier(profile, identifier):
    return bool(identifier) and (profile.get("name") == identifier or profile.get("address") == identifier)


def resolve_default_profile(parsed, profiles):
    if parsed.get("defaultProfile"):
        current = next((profile for profile in profiles if matches_identifier(profile, parsed.get("defaultProfile"))), None)
        if current:
            return current
    if len(profiles) == 1:
        return profiles[0]
    return None

version = sys.version_info
if version < (3, 9):
    issues.append(f"Python {version.major}.{version.minor} detected. Python 3.9+ is recommended.")

if not store_path.exists():
    issues.append(f"Profile store not found: {store_path}")
else:
    try:
        parsed = json.loads(store_path.read_text(encoding="utf-8"))
        profiles = parsed.get("profiles", []) if isinstance(parsed.get("profiles"), list) else []
        if not profiles:
            issues.append("No profiles stored.")
        if len(profiles) > 1 and not parsed.get("defaultProfile"):
            issues.append("Multiple profiles exist but no default profile is selected.")
        if parsed.get("defaultProfile") and not next((profile for profile in profiles if matches_identifier(profile, parsed.get("defaultProfile"))), None):
            issues.append(f"Default profile not found: {parsed.get('defaultProfile')}")
        active = resolve_default_profile(parsed, profiles)
        if active:
            for field in ("publicKey", "privateKey"):
                if not active.get(field):
                    issues.append(f"Active profile is missing {field}.")
            if not active.get("address"):
                warnings.append("Active profile has no address yet. This is normal before create_mailbox without a custom address.")
    except json.JSONDecodeError:
        issues.append(f"Profile store is not valid JSON: {store_path}")

if issues:
    print("Doctor check found issues:")
    for issue in issues:
        print(f"- {issue}")
    raise SystemExit(1)

for warning in warnings:
    print(f"Warning: {warning}")
print("Doctor check passed.")
