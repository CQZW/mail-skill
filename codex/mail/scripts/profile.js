#!/usr/bin/env node

const { generateKeyPairSync } = require("node:crypto");
const { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } = require("node:fs");
const { homedir } = require("node:os");
const { dirname, join, resolve } = require("node:path");

const STORE_PATH = process.env.FROMAIAGENT_PROFILE_STORE_PATH?.trim() || join(homedir(), ".fromaiagent", "profiles.json");

function readJsonFile(filePath) {
  return JSON.parse(readFileSync(resolve(filePath), "utf8"));
}

function emptyStore() {
  return { version: 1, profiles: [] };
}

function normalizeAddress(value) {
  return typeof value === "string" && value.trim() ? value.trim().toLowerCase() : "";
}

function displayAddress(profile) {
  return profile.address || "unassigned";
}

function profileIdentifier(profile) {
  return profile.address || profile.name;
}

function matchesIdentifier(profile, identifier) {
  return Boolean(identifier) && (profile.name === identifier || profile.address === identifier);
}

function normalizeProfile(candidate) {
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
    throw new Error("Profile must be a JSON object.");
  }

  const name = typeof candidate.name === "string" ? candidate.name.trim() : "";
  const publicKey = typeof candidate.publicKey === "string" ? candidate.publicKey.trim() : "";
  const privateKey = typeof candidate.privateKey === "string" ? candidate.privateKey.trim() : "";
  const address = normalizeAddress(candidate.address);

  if (!name) {
    throw new Error("Profile is missing name.");
  }
  if (!publicKey) {
    throw new Error(`Profile ${name} is missing publicKey.`);
  }
  if (!privateKey) {
    throw new Error(`Profile ${name} is missing privateKey.`);
  }

  const normalized = {
    name,
    publicKey,
    privateKey,
  };

  if (address) {
    normalized.address = address;
  }
  if (typeof candidate.guarantorAddress === "string" && candidate.guarantorAddress.trim()) {
    normalized.guarantorAddress = candidate.guarantorAddress.trim().toLowerCase();
  }
  if (typeof candidate.notes === "string" && candidate.notes.trim()) {
    normalized.notes = candidate.notes.trim();
  }

  return normalized;
}

function readStore() {
  if (!existsSync(STORE_PATH)) {
    return emptyStore();
  }
  const raw = readFileSync(STORE_PATH, "utf8").trim();
  if (!raw) {
    return emptyStore();
  }
  const parsed = JSON.parse(raw);
  return {
    version: 1,
    defaultProfile: typeof parsed.defaultProfile === "string" ? parsed.defaultProfile : undefined,
    profiles: Array.isArray(parsed.profiles) ? parsed.profiles.map(normalizeProfile) : [],
  };
}

function writeStore(store) {
  mkdirSync(dirname(STORE_PATH), { recursive: true });
  const tempPath = join(dirname(STORE_PATH), `.profiles.${process.pid}.${Date.now()}.tmp`);
  writeFileSync(tempPath, JSON.stringify(store, null, 2), "utf8");
  renameSync(tempPath, STORE_PATH);
}

function findProfile(store, identifier) {
  return store.profiles.find((profile) => matchesIdentifier(profile, identifier));
}

function resolveDefaultProfile(store) {
  if (store.defaultProfile) {
    return store.profiles.find((profile) => matchesIdentifier(profile, store.defaultProfile)) || null;
  }
  if (store.profiles.length === 1) {
    return store.profiles[0];
  }
  return null;
}

function ensureNoConflict(store, candidate) {
  if (store.profiles.some((profile) => profile.name === candidate.name)) {
    throw new Error(`Duplicate profile name: ${candidate.name}`);
  }
  if (candidate.address && store.profiles.some((profile) => profile.address && profile.address === candidate.address)) {
    throw new Error(`Duplicate profile address: ${candidate.address}`);
  }
}

function base64UrlToBase64(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  return normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
}

function exportRawPublicKey(publicKey) {
  try {
    const jwk = publicKey.export({ format: "jwk" });
    if (jwk && typeof jwk.x === "string") {
      return base64UrlToBase64(jwk.x);
    }
  } catch {
    // Fall back to extracting the raw Ed25519 key bytes from SPKI DER.
  }

  const spkiDer = publicKey.export({ format: "der", type: "spki" });
  return Buffer.from(spkiDer.subarray(-32)).toString("base64");
}

function createGeneratedProfile(name, addressInput) {
  const normalizedName = typeof name === "string" ? name.trim() : "";
  if (!normalizedName) {
    throw new Error("Missing profile name.");
  }

  const address = normalizeAddress(addressInput);
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const profile = {
    name: normalizedName,
    publicKey: exportRawPublicKey(publicKey),
    privateKey: Buffer.from(privateKey.export({ format: "der", type: "pkcs8" })).toString("base64"),
  };

  if (address) {
    profile.address = address;
  }

  return profile;
}

function listProfiles() {
  const store = readStore();
  if (store.profiles.length === 0) {
    console.log("No profiles stored.");
    return;
  }
  for (const profile of store.profiles) {
    const marker = matchesIdentifier(profile, store.defaultProfile) ? "*" : " ";
    console.log(`${marker} ${profile.name} <${displayAddress(profile)}>`);
  }
}

function showProfile(identifier) {
  const store = readStore();
  const profile = findProfile(store, identifier);
  if (!profile) {
    throw new Error(`Profile not found: ${identifier}`);
  }
  console.log(JSON.stringify(profile, null, 2));
}

function useProfile(identifier) {
  const store = readStore();
  const profile = findProfile(store, identifier);
  if (!profile) {
    throw new Error(`Profile not found: ${identifier}`);
  }
  store.defaultProfile = profileIdentifier(profile);
  writeStore(store);
  console.log(`Default profile set to ${profile.name} <${displayAddress(profile)}>`);
}

function addProfile(filePath) {
  const store = readStore();
  const profile = normalizeProfile(readJsonFile(filePath));
  ensureNoConflict(store, profile);
  store.profiles.push(profile);
  if (!store.defaultProfile) {
    store.defaultProfile = profileIdentifier(profile);
  }
  writeStore(store);
  console.log(`Added profile ${profile.name} <${displayAddress(profile)}>`);
}

function createProfile(name, address) {
  const store = readStore();
  const profile = createGeneratedProfile(name, address);
  ensureNoConflict(store, profile);
  store.profiles.push(profile);
  if (!store.defaultProfile) {
    store.defaultProfile = profileIdentifier(profile);
  }
  writeStore(store);
  console.log(`Created profile ${profile.name} <${displayAddress(profile)}>`);
}

function importProfiles(filePath) {
  const store = readStore();
  const imported = readJsonFile(filePath);
  const profiles = Array.isArray(imported.profiles) ? imported.profiles.map(normalizeProfile) : [];
  for (const profile of profiles) {
    ensureNoConflict(store, profile);
    store.profiles.push(profile);
  }
  if (typeof imported.defaultProfile === "string" && imported.defaultProfile.trim()) {
    store.defaultProfile = imported.defaultProfile.trim();
  } else if (!store.defaultProfile && store.profiles[0]) {
    store.defaultProfile = profileIdentifier(store.profiles[0]);
  }
  writeStore(store);
  console.log(`Imported ${profiles.length} profile(s).`);
}

function exportProfiles(identifier) {
  const store = readStore();
  if (!identifier) {
    console.log(JSON.stringify(store, null, 2));
    return;
  }
  const profile = findProfile(store, identifier);
  if (!profile) {
    throw new Error(`Profile not found: ${identifier}`);
  }
  console.log(JSON.stringify(profile, null, 2));
}

function removeProfile(identifier, force) {
  const store = readStore();
  const index = store.profiles.findIndex((profile) => matchesIdentifier(profile, identifier));
  if (index === -1) {
    throw new Error(`Profile not found: ${identifier}`);
  }
  const profile = store.profiles[index];
  if (store.defaultProfile === profileIdentifier(profile) && !force) {
    throw new Error(`Cannot remove the default profile without --force: ${profile.name}`);
  }
  store.profiles.splice(index, 1);
  if (store.defaultProfile === profileIdentifier(profile)) {
    store.defaultProfile = store.profiles[0] ? profileIdentifier(store.profiles[0]) : undefined;
  }
  writeStore(store);
  console.log(`Removed profile ${profile.name} <${displayAddress(profile)}>`);
}

function assignAddress(identifier, addressInput) {
  const store = readStore();
  const profile = findProfile(store, identifier);
  if (!profile) {
    throw new Error(`Profile not found: ${identifier}`);
  }
  const address = normalizeAddress(addressInput);
  if (!address) {
    throw new Error("Missing mailbox address.");
  }
  const conflicting = store.profiles.find((item) => item !== profile && item.address === address);
  if (conflicting) {
    throw new Error(`Duplicate profile address: ${address}`);
  }
  profile.address = address;
  if (!store.defaultProfile) {
    store.defaultProfile = profileIdentifier(profile);
  }
  writeStore(store);
  console.log(`Assigned address ${address} to ${profile.name}.`);
}

const [, , command, ...rest] = process.argv;

try {
  switch (command) {
    case "list":
      listProfiles();
      break;
    case "show":
      showProfile(rest[0]);
      break;
    case "use":
      useProfile(rest[0]);
      break;
    case "add":
      addProfile(rest[0]);
      break;
    case "create":
      createProfile(rest[0], rest[1]);
      break;
    case "import":
      importProfiles(rest[0]);
      break;
    case "export":
      exportProfiles(rest[0]);
      break;
    case "remove":
      removeProfile(rest.find((item) => !item.startsWith("--")), rest.includes("--force"));
      break;
    case "assign-address":
      assignAddress(rest[0], rest[1]);
      break;
    default:
      console.error("Usage: profile.js <list|show|use|add|create|import|export|remove|assign-address> [...]");
      process.exit(1);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
