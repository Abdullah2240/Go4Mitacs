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
    expect(body.items.every((item: { score: number }) => item.score >= 0 && item.score <= 100)).toBe(true);
    expect(body.items.some((item: { score: number }) => item.score === 100)).toBe(false);
    expect(body.method).toBe("deterministic-full-corpus-bm25-retrieval");
    expect(body.items.flatMap((item: { matched_evidence: string[] }) => item.matched_evidence)).not.toContain("and");
    expect(body.items.every((item: { source_url: string }) => item.source_url === "https://globalink.mitacs.ca/")).toBe(true);
  });

  it("does not penalize a long CV padded with real, in-corpus vocabulary relative to a short snippet for the same project match", async () => {
    const shortEvidence = "Python data analysis";
    const cvNoise = "communication teamwork leadership project management stakeholder engagement research writing presentation collaboration mentoring";
    const longEvidence = shortEvidence + " " + cvNoise;
    const shortResponse = await matches(new Request("http://localhost/api/local/matches?limit=50", { method: "POST", headers: { "content-type": "application/json", "content-length": "9999" }, body: JSON.stringify({ evidence_text: shortEvidence }) }) as any);
    const longResponse = await matches(new Request("http://localhost/api/local/matches?limit=50", { method: "POST", headers: { "content-type": "application/json", "content-length": "9999" }, body: JSON.stringify({ evidence_text: longEvidence }) }) as any);
    const shortBody = await shortResponse.json();
    const longBody = await longResponse.json();
    const findCoverage = (body: any, projectId: string) => body.items.find((item: { project_id: string }) => item.project_id === projectId)?.score_breakdown?.evidence_coverage ?? 0;
    const sharedIds = shortBody.items.map((item: { project_id: string }) => item.project_id).filter((id: string) => longBody.items.some((item: { project_id: string }) => item.project_id === id));
    expect(sharedIds.length).toBeGreaterThan(0);
    for (const id of sharedIds) {
      expect(findCoverage(longBody, id)).toBeGreaterThanOrEqual(findCoverage(shortBody, id) - 0.01);
    }
  });
});
