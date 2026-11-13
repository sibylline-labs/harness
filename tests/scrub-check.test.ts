import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { denylistHits, hashTerm, readDenylist, scan, tokens } from "../scripts/scrub-check";

// Flagged values are built at runtime so this file never holds one.
const term = ["ac", "me"].join("");
const pair = ["acme", "corp"].join("-");
const deny = new Set([hashTerm(term), hashTerm(pair)]);
const rules = (path: string, text: string) => scan(path, text, { denylist: deny }).map((h) => h.rule);

describe("tokens", () => {
  // admits: a glued, camel, fullwidth or zero-width-split name escaping the denylist; tokenizing is runtime text handling no type sees.
  test("splits case, digit and separator boundaries, NFKC, zero-width", () => {
    expect(tokens("AcmeApi")).toEqual(["acme", "api"]);
    expect(tokens("acme2go")).toEqual(["acme", "2", "go"]);
    expect(tokens("ACMEService")).toEqual(["acme", "service"]);
    expect(tokens("ａｃｍｅ")).toEqual(["acme"]);
    expect(tokens("ac​me")).toEqual(["acme"]);
    expect(tokens("acme_corp/x")).toEqual(["acme", "corp", "x"]);
  });
  // admits: a denylist term no lookup can ever match being added silently.
  test("a term of three tokens is refused", () => {
    expect(() => hashTerm("a-b-c")).toThrow();
  });
});

describe("denylist", () => {
  // admits: a denylisted term in a common identifier form passing, or a longer word falsely flagged.
  test.each([
    [term, true],
    [`${term.toUpperCase()}_API_KEY`, true],
    [`${term[0]!.toUpperCase()}${term.slice(1)}Service`, true],
    [`see ${pair} docs`, true],
    [`see acme_corp docs`, true],
    [`${term}s and ${term}ish`, false],
    ["acmecorp", false],
  ])("%s → %p", (line, flagged) => {
    expect(denylistHits(line, deny).length > 0).toBe(flagged);
  });
  // admits: a name in a directory or file name slipping past a content-only scan.
  test("paths are scanned", () => {
    expect(rules(`skills/${term}-x/SKILL.md`, "clean")).toContain("denylist");
  });
  // admits: a plaintext term landing in the shipped hash list, which would publish the name.
  test("the shipped list holds only hashes", () => {
    const text = readFileSync(new URL("../scripts/scrub-denylist.sha256", import.meta.url), "utf8");
    expect(readDenylist(text).size).toBeGreaterThan(0);
    for (const l of text.split("\n")) expect(l === "" || l.startsWith("#") || /^[0-9a-f]{64}$/.test(l)).toBe(true);
  });
});

describe("rules", () => {
  const key = ["ZZQ", "12"].join("-");
  // admits: a private tracker key, link, label, address, home path or token reaching a public file.
  test.each([
    ["tracker key", `fixes ${key}`, "tracker-label"],
    ["tracker link", ["linear", "app/x/issue"].join(".") + "/1", "tracker-workspace"],
    ["requirements label", ["PRD", "X-D6"].join("-"), "requirements-label"],
    ["private org", ["sibylline", "advisory"].join("-"), "private-org"],
    ["email", ["dev", "corp.io"].join("@"), "email"],
    ["home path", "/Users/" + "jdoe/x", "home-path"],
    ["git host other than github", ["git", "gitlab.corp.io:x"].join("@"), "email"],
    ["token", ["ghp", "a".repeat(36)].join("_"), "token-shaped"],
    ["pr reference", ["PR", "#12"].join(" "), "private-pr"],
  ])("flags a %s", (_name, line, rule) => {
    expect(rules("x.md", line)).toContain(rule);
  });
  // admits: a standard, the public org or a placeholder being flagged, which would train contributors to ignore the gate.
  test.each([
    ["a standard", "RFC-9110 and UTF-8 and HTTP-2"],
    ["the public org", "sibylline-labs/harness"],
    ["an example address", "dev@example.com"],
    ["github ssh", "git@github.com:org/repo.git"],
    ["a placeholder home", "/home/runner/work and /Users/me/x"],
    ["a placeholder key", "ABC-123 and PROJ-42"],
  ])("allows %s", (_name, line) => {
    expect(rules("x.md", line)).toEqual([]);
  });
  // admits: the contact domain spreading beyond the contact files.
  test("the contact domain only in the contact files", () => {
    const addr = ["security", "sibylline.group"].join("@");
    expect(rules("SECURITY.md", addr)).toEqual([]);
    expect(rules("skills/x/SKILL.md", addr)).not.toEqual([]);
  });
});
