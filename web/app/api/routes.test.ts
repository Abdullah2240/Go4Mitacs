import { describe, expect, it } from "vitest";
import { GET as health } from "./health/route";
import { GET as projects } from "./projects/route";
import { GET as detail } from "./projects/[projectId]/route";
import { POST as matches } from "./local/matches/route";

describe("same-origin public routes", () => {
  it("reports the complete public corpus", async () => {
    const response = health();
    expect((await response.json()).corpus_count).toBe(3359);
  });

  it("searches compact project pages", async () => {
    const response = projects({ nextUrl: new URL("http://localhost/api/projects?q=hydro&limit=2") } as any);
    const body = await response.json();
    expect(body.items.length).toBeLessThanOrEqual(2);
    expect(body.corpus_version).toBeTruthy();
  });

  it("returns one project detail and 404 for unknown IDs", async () => {
    const response = detail(new Request("http://localhost/api/projects/51146"), { params: { projectId: "51146" } });
    expect((await response.json()).id).toBe("51146");
    const missing = detail(new Request("http://localhost/api/projects/nope"), { params: { projectId: "nope" } });
    expect(missing.status).toBe(404);
  });

  it("screens all 3,359 projects before limiting results", async () => {
    const response = await matches(new Request("http://localhost/api/local/matches?limit=3", { method: "POST", headers: { "content-type": "application/json", "content-length": "42" }, body: JSON.stringify({ evidence_text: "Python data analysis" }) }) as any);
    const body = await response.json();
    expect(body.considered).toBe(3359);
    expect(body.items).toHaveLength(3);
    expect(body.method).toContain("full-corpus");
  });
});
