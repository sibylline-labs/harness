/**
 * scrub-check.ts — fail when the tree carries something a public template must not:
 * a private organisation reference, a tracker key or tracker link, a requirements label,
 * a personal email or home path, an internal host, a secret-store path, a commit SHA from
 * outside this repository, a token-shaped literal, or a term on the hashed denylist.
 *
 *   bun scripts/scrub-check.ts              scan every tracked or untracked, not-ignored
 *                                           file, its path included
 *   bun scripts/scrub-check.ts --history    also scan every blob, path and commit message
 *                                           reachable from HEAD; refuses a shallow clone
 *
 * Exits 1 and prints `where: [rule] text` per hit, 0 when clean, 2 when it cannot scan.
 *
 * The denylist (scripts/scrub-denylist.sha256) holds the sha256 of each term, never the
 * term: a public list of the names a fork must keep out would publish those names. Text is
 * NFKC-normalised, stripped of zero-width and soft-hyphen characters, split at case and
 * digit boundaries and at every non-alphanumeric run, and lower-cased. Each token
 * (unigram) and each adjacent pair joined by `-` (bigram) is hashed and looked up. A fork
 * adds its own terms with `bun scripts/scrub-check.ts --hash <term>`.
 *
 * Test fixtures that need a flagged value build it at runtime, so the source never holds it.
 */

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, lstatSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parseArgs } from "node:util";

const DENYLIST = "scripts/scrub-denylist.sha256";
/** Files whose text is detection patterns or hashes: only the path itself is scanned. */
const PATTERN_FILES = new Set(["scripts/scrub-check.ts", "tests/scrub-check.test.ts", DENYLIST]);
const LICENCE_FILES = new Set(["LICENSE", "NOTICE"]);
/** Files allowed to name the public contact domain and its mailboxes. */
const CONTACT_FILES = new Set(["README.md", "CONTRIBUTING.md", "SECURITY.md"]);
const CONTACT_ADDRESSES = new Set(["security@sibylline.group", "support@sibylline.group"]);
const SKIP = new Set(["bun.lock"]);

const EXAMPLE_DOMAIN = /(^|\.)(example\.(com|org|net)|example|test|invalid|localhost)$/i;
const ALLOWED_ADDRESSES = new Set(["noreply@anthropic.com", "noreply@github.com"]);
/** Public standards and documentation placeholders written `ABC-123`; any other such label is a tracker key. */
const STANDARD_PREFIXES = new Set([
  "ABC", "PROJ", "RFC", "UTF", "SHA", "ISO", "CVE", "CWE", "EIP", "ERC", "HTTP", "GPT", "AES", "PEP", "WCAG", "TLS", "ES", "UTC", "GMT",
]);
/** Placeholder account names a doc may put in a home path. */
const PLACEHOLDER_USERS = new Set(["me", "you", "user", "runner", "<user>", "$user", "name"]);

export type KnownShas = ReadonlySet<string>;
type Allow = (m: RegExpMatchArray, path: string, line: string, known: KnownShas) => boolean;
export type Rule = { id: string; re: RegExp; allow?: Allow };

export const RULES: readonly Rule[] = [
  {
    // The public org (`sibylline-labs`) is fine anywhere; the copyright holder only in the licence files.
    id: "private-org",
    re: /sibylline/gi,
    allow: (m, path, line) => {
      const rest = line.slice((m.index ?? 0) + m[0].length);
      if (/^-labs\b/i.test(rest)) return true;
      if (/^-labs\w/i.test(rest)) return path === "";
      if (/^\.group\b/i.test(rest)) return CONTACT_FILES.has(path);
      if (/^ labs\b/i.test(rest)) return LICENCE_FILES.has(path);
      return false;
    },
  },
  { id: "tracker-workspace", re: /linear\.app\//gi },
  { id: "internal-host", re: /\.svc\.cluster\.local|workers\.dev|\.run\.app\b|\.cloudfunctions\.net|\.appspot\.com/gi },
  { id: "bucket-path", re: /\b(gs|s3):\/\//gi },
  {
    id: "secret-store-path",
    re: /projects\/[^/\s]+\/secrets|secretmanager\.googleapis|gcloud secrets|keyRings\/|cryptoKeys\/|vault:\/\/|secret\/data\//gi,
  },
  {
    id: "email",
    re: /[A-Za-z0-9._%+-]+@((?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})\b/g,
    allow: (m, path) => {
      const [whole, domain] = m;
      if (CONTACT_ADDRESSES.has(whole.toLowerCase()) && CONTACT_FILES.has(path)) return true;
      if (whole.toLowerCase() === "git@github.com") return true;
      if (EXAMPLE_DOMAIN.test(domain!)) return true;
      return ALLOWED_ADDRESSES.has(whole.toLowerCase());
    },
  },
  {
    id: "home-path",
    re: /(?:\/Users|\/home)\/([^/\s`'")]+)\//g,
    allow: (m) => PLACEHOLDER_USERS.has(m[1]!.toLowerCase()),
  },
  { id: "tracker-label", re: /\b([A-Z]{2,6})-\d+\b/g, allow: (m) => STANDARD_PREFIXES.has(m[1]!) },
  { id: "requirements-label", re: /\bPRD-[A-Z0-9]/g },
  { id: "private-pr", re: /\bPR #\d+/g },
  {
    // A commit SHA cited as provenance. One this repository can resolve, or an action pin, is fine.
    id: "private-sha",
    re: /(?<![-0-9A-Za-z])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])(?:[0-9a-f]{40}|[0-9a-f]{7,12})(?![-0-9A-Za-z])/g,
    allow: (m, _path, _line, known) => {
      for (const k of known) if (k.startsWith(m[0])) return true;
      return false;
    },
  },
  {
    id: "token-shaped",
    re: new RegExp(
      [
        String.raw`\bgh[pousr]_[A-Za-z0-9]{36,}`,
        String.raw`\bgithub_pat_[A-Za-z0-9_]{22,}`,
        String.raw`\blin_(?:api|oauth)_[A-Za-z0-9]{20,}`,
        String.raw`\bglpat-[A-Za-z0-9_-]{20,}`,
        String.raw`\bnpm_[A-Za-z0-9]{36,}`,
        String.raw`\bhf_[A-Za-z0-9]{30,}`,
        String.raw`\b(?:AKIA|ASIA)[0-9A-Z]{16}\b`,
        String.raw`\bxox[baprs]-[0-9A-Za-z-]{10,}`,
        String.raw`\b[sr]k_(?:live|test)_[0-9A-Za-z]{10,}`,
        String.raw`\bsk-[A-Za-z0-9_-]{20,}`,
        String.raw`\bAIza[0-9A-Za-z_-]{35}`,
        String.raw`\beyJ[A-Za-z0-9_-]{10,}`,
        String.raw`-----BEGIN [A-Z ]*PRIVATE KEY-----`,
      ].join("|"),
      "g",
    ),
  },
];

const sha256 = (s: string): string => createHash("sha256").update(s).digest("hex");

/** The tokens the denylist sees in `text`, in order. */
export function tokens(text: string): string[] {
  return text
    .normalize("NFKC")
    .replace(/[­​-‍⁠﻿]/g, "")
    .replace(/([\p{Ll}\p{N}])(\p{Lu})/gu, "$1 $2")
    .replace(/(\p{Lu})(\p{Lu}\p{Ll})/gu, "$1 $2")
    .replace(/(\p{L})(\p{N})/gu, "$1 $2")
    .replace(/(\p{N})(\p{L})/gu, "$1 $2")
    .toLowerCase()
    .split(/[^\p{L}\p{N}]+/u)
    .filter(Boolean);
}

/** The hash a denylist line holds for `term`; refuses a term of more than two tokens, which no lookup can match. */
export function hashTerm(term: string): string {
  const t = tokens(term);
  if (t.length === 0 || t.length > 2) throw new Error(`a denylist term is one or two tokens, not ${JSON.stringify(term)}`);
  return sha256(t.join("-"));
}

export function readDenylist(text: string): Set<string> {
  return new Set(
    text
      .split("\n")
      .map((l) => l.replace(/#.*/, "").trim())
      .filter((l) => /^[0-9a-f]{64}$/.test(l)),
  );
}

/** The denylisted unigrams and bigrams in one line. */
export function denylistHits(line: string, hashes: ReadonlySet<string>): string[] {
  if (hashes.size === 0) return [];
  const t = tokens(line);
  const hits: string[] = [];
  t.forEach((tok, i) => {
    if (hashes.has(sha256(tok))) hits.push(tok);
    const next = t[i + 1];
    if (next !== undefined && hashes.has(sha256(`${tok}-${next}`))) hits.push(`${tok}-${next}`);
  });
  return hits;
}

export type Hit = { where: string; rule: string; text: string };

export interface ScanOptions {
  where?: string;
  known?: KnownShas;
  denylist?: ReadonlySet<string>;
  /** Only the denylist and the path run (a pattern file's own text). */
  pathOnly?: boolean;
}

/** Every hit in one file's text; `path` is repo-relative, or empty for a commit message. */
export function scan(path: string, text: string, opts: ScanOptions = {}): Hit[] {
  const { where = path, known = new Set<string>(), denylist = new Set<string>(), pathOnly = false } = opts;
  const hits: Hit[] = [];
  const lines = pathOnly ? [] : text.split("\n");
  lines.forEach((line, i) => {
    const at = `${where}:${i + 1}`;
    for (const rule of RULES) {
      for (const m of line.matchAll(rule.re)) {
        if (!rule.allow?.(m, path, line, known)) hits.push({ where: at, rule: rule.id, text: line.trim() });
      }
    }
    for (const term of denylistHits(line, denylist)) hits.push({ where: at, rule: "denylist", text: term });
  });
  if (path !== "") {
    for (const term of denylistHits(path, denylist)) hits.push({ where: `${where} (path)`, rule: "denylist", text: term });
    for (const rule of RULES) {
      for (const m of path.matchAll(rule.re)) {
        if (!rule.allow?.(m, path, path, known)) hits.push({ where: `${where} (path)`, rule: rule.id, text: path });
      }
    }
  }
  return hits;
}

function git(...args: string[]): string {
  const r = spawnSync("git", args, { encoding: "utf8", maxBuffer: 1 << 30 });
  if (r.status !== 0) throw new Error(`git ${args.join(" ")}: ${r.stderr}`);
  return r.stdout;
}

function knownShas(): Set<string> {
  const known = new Set(git("rev-list", "HEAD").split("\n").filter(Boolean));
  // An action pin or a `<NAME>_REF:` pin in any version of a workflow names a public commit, so a
  // superseded pin still in history is not a private SHA.
  const PIN = /(?:\buses:\s*\S+@|#|\b[A-Z_]+_REF:\s*)([0-9a-f]{40})\b/g;
  const dir = ".github/workflows";
  const texts = existsSync(dir) ? readdirSync(dir).map((f) => readFileSync(join(dir, f), "utf8")) : [];
  texts.push(git("log", "-p", "--format=", "HEAD", "--", dir));
  for (const text of texts) for (const m of text.matchAll(PIN)) known.add(m[1]!);
  return known;
}

const isText = (buf: Buffer) => !buf.subarray(0, 8000).includes(0);

function scanTree(known: KnownShas, denylist: ReadonlySet<string>): Hit[] {
  return git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    .split("\0")
    .filter((p) => p && !SKIP.has(p) && lstatSync(p, { throwIfNoEntry: false })?.isFile())
    .flatMap((p) => {
      const buf = readFileSync(p);
      return isText(buf) ? scan(p, buf.toString("utf8"), { known, denylist, pathOnly: PATTERN_FILES.has(p) }) : scan(p, "", { known, denylist, pathOnly: true });
    });
}

function scanHistory(known: KnownShas, denylist: ReadonlySet<string>): Hit[] {
  const hits: Hit[] = [];
  const seen = new Set<string>();
  for (const row of git("rev-list", "--objects", "HEAD").split("\n")) {
    const [sha, path] = row.split(" ");
    if (!sha || !path || seen.has(sha) || SKIP.has(path)) continue;
    seen.add(sha);
    if (git("cat-file", "-t", sha).trim() !== "blob") continue;
    const text = git("cat-file", "-p", sha);
    const where = `${sha.slice(0, 10)}:${path}`;
    hits.push(...scan(path, text.includes("\0") ? "" : text, { where, known, denylist, pathOnly: PATTERN_FILES.has(path) || text.includes("\0") }));
  }
  for (const commit of git("rev-list", "HEAD").split("\n").filter(Boolean)) {
    hits.push(...scan("", git("log", "-1", "--format=%B", commit), { where: `commit ${commit.slice(0, 10)}`, known, denylist }));
  }
  return hits;
}

function main(): number {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: { history: { type: "boolean", default: false }, hash: { type: "string" } },
    strict: true,
  });
  if (values.hash !== undefined) {
    console.log(hashTerm(values.hash));
    return 0;
  }
  if (!existsSync(DENYLIST)) {
    console.error(`scrub-check: no denylist at ${DENYLIST}`);
    return 2;
  }
  if (values.history && git("rev-parse", "--is-shallow-repository").trim() === "true") {
    console.error("scrub-check: this clone is shallow, so --history cannot see every commit; fetch the full history (actions/checkout: fetch-depth: 0)");
    return 2;
  }
  const denylist = readDenylist(readFileSync(DENYLIST, "utf8"));
  const known = knownShas();
  const hits = values.history ? [...scanTree(known, denylist), ...scanHistory(known, denylist)] : scanTree(known, denylist);
  for (const h of hits) console.log(`${h.where}: [${h.rule}] ${h.text}`);
  console.error(hits.length ? `scrub-check: ${hits.length} hit(s)` : "scrub-check: clean");
  return hits.length ? 1 : 0;
}

if (import.meta.main) process.exit(main());
