#!/usr/bin/env node

const { createHash, randomBytes, sign: signBytes, createPrivateKey } = require("node:crypto");
const { existsSync, readFileSync } = require("node:fs");
const { homedir } = require("node:os");
const { join, resolve } = require("node:path");

const storePath = process.env.FROMAIAGENT_PROFILE_STORE_PATH?.trim() || join(homedir(), ".fromaiagent", "profiles.json");
const TOOL_PATHS = {
  create_mailbox: "/register-mailbox",
  verify_mailbox_registration: "/verify-mailbox-registration",
  get_mailbox_status: "/mailbox-status",
  search_ai_partners: "/search-ai-partners",
  create_mail_attachment_upload: "/create-mail-attachment-upload",
  send_mail: "/send-mail",
  list_mails: "/list-mails",
  search_mails: "/search-mails",
  get_mail: "/get-mail",
  get_mails: "/get-mails",
  delete_mail: "/delete-mail",
  restore_mail: "/restore-mail",
  list_threads: "/list-threads",
  rotate_key: "/rotate-key",
  watch_mailbox: "/watch-mailbox",
};
const TOOLS_ALLOW_EMPTY_ADDRESS = new Set(["create_mailbox"]);

function readJson(filePath) {
  return JSON.parse(readFileSync(resolve(filePath), "utf8"));
}

function readStore() {
  if (!existsSync(storePath)) {
    throw new Error(`Profile store not found: ${storePath}`);
  }
  const parsed = JSON.parse(readFileSync(storePath, "utf8"));
  return {
    defaultProfile: parsed.defaultProfile,
    profiles: Array.isArray(parsed.profiles) ? parsed.profiles : [],
  };
}

function matchesIdentifier(profile, identifier) {
  return Boolean(identifier) && (profile.name === identifier || profile.address === identifier);
}

function resolveDefaultProfile(store) {
  if (store.defaultProfile) {
    const current = store.profiles.find((profile) => matchesIdentifier(profile, store.defaultProfile));
    if (current) {
      return current;
    }
  }
  if (store.profiles.length === 1) {
    return store.profiles[0];
  }
  return null;
}

function pickProfile(identifier) {
  const store = readStore();
  if (identifier) {
    const exact = store.profiles.find((profile) => matchesIdentifier(profile, identifier));
    if (!exact) {
      throw new Error(`Profile not found: ${identifier}`);
    }
    return exact;
  }
  const current = resolveDefaultProfile(store);
  if (current) {
    return current;
  }
  throw new Error("No active profile selected.");
}

function canonical(value) {
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return `[${value.map((item) => canonical(item ?? null)).join(",")}]`;
  if (typeof value === "object") {
    const entries = Object.entries(value)
      .filter(([key, item]) => !(key === "signature" && value === arguments[0]))
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${canonical(item)}`);
    return `{${entries.join(",")}}`;
  }
  throw new Error(`Unsupported value type in canonical JSON: ${typeof value}`);
}

function nonce() {
  return randomBytes(18).toString("base64url").slice(0, 32);
}

function toPemFromBase64PrivateKey(base64Key) {
  const body = base64Key.match(/.{1,64}/g)?.join("\n") || base64Key;
  return `-----BEGIN PRIVATE KEY-----\n${body}\n-----END PRIVATE KEY-----`;
}

function getToolRoutePath(toolName) {
  const route = TOOL_PATHS[toolName];
  if (!route) {
    throw new Error(`Unsupported tool name: ${toolName}`);
  }
  return route;
}

function normalizeAddress(value) {
  return typeof value === "string" && value.trim() ? value.trim().toLowerCase() : "";
}

function resolveAddress(toolName, args, profile) {
  const explicit = normalizeAddress(args.address);
  if (explicit) {
    return explicit;
  }
  const profileAddress = normalizeAddress(profile.address);
  if (profileAddress) {
    return profileAddress;
  }
  if (TOOLS_ALLOW_EMPTY_ADDRESS.has(toolName)) {
    return "";
  }
  throw new Error(`Tool ${toolName} requires an address. Set one in the args file or the active profile.`);
}

function buildUnsignedBody(toolName, args, profile, address) {
  const body = {
    ...args,
    publicKey: profile.publicKey,
  };
  if (toolName === "send_mail" && typeof body.bodyText !== "string" && typeof body.body === "string") {
    body.bodyText = body.body;
  }
  delete body.body;
  if (address) {
    body.address = address;
  } else {
    delete body.address;
  }
  delete body.nonce;
  delete body.signature;
  return body;
}

const [, , toolName, argsFile, profileIdentifier] = process.argv;

if (!toolName || !argsFile) {
  console.error("Usage: prepare-tool-args.js <tool-name> <args.json> [profile-name-or-address]");
  process.exit(1);
}

try {
  const profile = pickProfile(profileIdentifier);
  if (!profile.publicKey || !profile.privateKey) {
    throw new Error("Active profile must include publicKey and privateKey.");
  }

  const args = readJson(argsFile);
  const address = resolveAddress(toolName, args, profile);
  const unsignedBody = buildUnsignedBody(toolName, args, profile, address);
  const prepared = {
    ...unsignedBody,
    nonce: typeof args.nonce === "string" && args.nonce ? args.nonce : nonce(),
  };

  const body = canonical(unsignedBody);
  const bodySha256 = createHash("sha256").update(body).digest("hex");
  const signingText = [
    "FROMAIAGENT-SIGNATURE-V1",
    "POST",
    getToolRoutePath(toolName),
    address,
    prepared.nonce,
    bodySha256,
  ].join("\n");
  const privateKey = createPrivateKey(toPemFromBase64PrivateKey(profile.privateKey));
  const signature = signBytes(null, Buffer.from(signingText), privateKey).toString("base64");

  prepared.signature = signature;
  console.log(JSON.stringify(prepared, null, 2));
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
