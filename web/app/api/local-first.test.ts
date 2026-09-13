import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const APP_DIR = join(__dirname, "..");
const API_DIR = __dirname;

function walk(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

function routeHandlerFiles(): string[] {
  return walk(API_DIR).filter((file) => /[\\/]route\.tsx?$/.test(file));
}

function sourceFiles(dir: string): string[] {
  return walk(dir).filter((file) => /\.tsx?$/.test(file) && !/\.test\.tsx?$/.test(file));
}

/**
 * Local-first is the product constraint this app is built around: matching runs in
 * the browser, and user evidence plus BYOK provider keys never reach our server.
 *
 * The Python suite in ../../tests/test_local_first.py guards the legacy FastAPI app
 * in api/, which is not deployed. These tests guard the Next.js app that actually
 * ships on Vercel.
 */
describe("local-first constraint (deployed Next.js app)", () => {
  it("exposes only the known read-only routes", () => {
    const routes = routeHandlerFiles()
      .map((file) => file.slice(API_DIR.length).replace(/\\/g, "/").replace(/\/route\.tsx?$/, ""))
      .sort();

    // Adding a route here is a deliberate act: anything that accepts user evidence or
    // an API key and forwards it onward breaks the local-first guarantee.
    expect(routes).toEqual([
      "/health",
      "/local/matches",
      "/projects",
      "/projects/[projectId]",
    ]);
  });

  it("has no server route that calls an external service", () => {
    for (const file of routeHandlerFiles()) {
      const source = readFileSync(file, "utf8");
      expect(source, `${file} must not perform network calls`).not.toMatch(/\bfetch\s*\(/);
      expect(source, `${file} must not import an HTTP client`).not.toMatch(
        /from\s+["'](axios|node-fetch|undici|got|openai|@google\/generative-ai|@huggingface)/,
      );
    }
  });

  it("has no server route that reads provider credentials from the environment", () => {
    for (const file of routeHandlerFiles()) {
      const source = readFileSync(file, "utf8");
      expect(source, `${file} must not read API keys from env`).not.toMatch(
        /process\.env\.[A-Z_]*(KEY|TOKEN|SECRET|CREDENTIAL)/,
      );
    }
  });

  it("sends provider traffic only to known provider origins, from client code", () => {
    const allowedHosts = [
      "openrouter.ai",
      "generativelanguage.googleapis.com",
      "api.openai.com",
      "api-inference.huggingface.co",
    ];

    const callers = sourceFiles(join(APP_DIR, "..", "lib"))
      .concat(sourceFiles(APP_DIR))
      .filter((file) => /\bfetch\s*\(/.test(readFileSync(file, "utf8")));

    expect(callers.length, "expected at least one client-side provider caller").toBeGreaterThan(0);

    for (const file of callers) {
      const source = readFileSync(file, "utf8");
      const urls = source.match(/https:\/\/[a-z0-9.-]+/gi) ?? [];
      for (const url of urls) {
        const host = url.replace(/^https:\/\//i, "");
        expect(
          allowedHosts.some((allowed) => host === allowed || host.endsWith(`.${allowed}`)),
          `${file} targets unexpected host ${host}`,
        ).toBe(true);
      }
    }
  });

  it("never persists evidence or keys to server-side storage", () => {
    for (const file of routeHandlerFiles()) {
      const source = readFileSync(file, "utf8");
      expect(source, `${file} must not write to the filesystem`).not.toMatch(
        /from\s+["']node:fs["']|require\(["']fs["']\)|writeFileSync|appendFileSync/,
      );
      expect(source, `${file} must not log request bodies`).not.toMatch(/console\.(log|info|warn|error)/);
    }
  });
});
