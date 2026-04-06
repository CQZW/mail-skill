#!/usr/bin/env node

const { existsSync, readFileSync } = require("node:fs");
const { homedir } = require("node:os");
const { join } = require("node:path");

const storePath = process.env.FROMAIAGENT_PROFILE_STORE_PATH?.trim() || join(homedir(), ".fromaiagent", "profiles.json");
const major = Number.parseInt(process.versions.node.split(".")[0] || "0", 10);

const issues = [];
const warnings = [];

function matchesIdentifier(profile, identifier) {
  return Boolean(identifier) && (profile.name === identifier || profile.address === identifier);
}

function resolveDefaultProfile(parsed, profiles) {
  if (parsed.defaultProfile) {
    return profiles.find((profile) => matchesIdentifier(profile, parsed.defaultProfile)) || null;
  }
  return profiles.length === 1 ? profiles[0] : null;
}

if (major < 22) {
  issues.push(`Node.js ${process.versions.node} detected. Node 22.6+ is recommended.`);
}

if (!existsSync(storePath)) {
  issues.push(`Profile store not found: ${storePath}`);
} else {
  try {
    const parsed = JSON.parse(readFileSync(storePath, "utf8"));
    const profiles = Array.isArray(parsed.profiles) ? parsed.profiles : [];
    if (profiles.length === 0) {
      issues.push("No profiles stored.");
    }
    if (profiles.length > 1 && !parsed.defaultProfile) {
      issues.push("Multiple profiles exist but no default profile is selected.");
    }
    if (parsed.defaultProfile && !profiles.find((profile) => matchesIdentifier(profile, parsed.defaultProfile))) {
      issues.push(`Default profile not found: ${parsed.defaultProfile}`);
    }
    const active = resolveDefaultProfile(parsed, profiles);
    if (active) {
      for (const field of ["publicKey", "privateKey"]) {
        if (!active[field]) {
          issues.push(`Active profile is missing ${field}.`);
        }
      }
      if (!active.address) {
        warnings.push("Active profile has no address yet. This is normal before create_mailbox without a custom address.");
      }
    }
  } catch {
    issues.push(`Profile store is not valid JSON: ${storePath}`);
  }
}

if (issues.length === 0) {
  for (const warning of warnings) {
    console.log(`Warning: ${warning}`);
  }
  console.log("Doctor check passed.");
} else {
  console.log("Doctor check found issues:");
  for (const issue of issues) {
    console.log(`- ${issue}`);
  }
  process.exitCode = 1;
}
