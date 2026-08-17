import { describe, expect, it } from "vitest";
import { buildLocalProfile } from "./profile";

describe("deterministic local profile", () => {
  it("extracts evidence vocabulary without inventing metrics", () => {
    const profile = buildLocalProfile([{ id: "1", name: "notes.txt", type: "TXT", chars: 80, size: 80, hash: "x", status: "ready", createdAt: "now", text: "Built a Python data analysis pipeline with pandas and regression modelling for transport research." }]);
    expect(profile.skills).toContain("python");
    expect(profile.tools).toContain("pandas");
    expect(profile.domains).toContain("transport");
    expect(profile.evidence.join(" ")).not.toContain("76%");
  });

  it("excludes private reference documents from the candidate profile", () => {
    const profile = buildLocalProfile([
      { id: "candidate", name: "cv.txt", type: "TXT", chars: 20, size: 20, hash: "a", status: "ready", createdAt: "now", text: "Python data analysis" },
      { id: "reference", name: "private.pdf", type: "PDF", chars: 40, size: 40, hash: "b", status: "ready", createdAt: "now", kind: "reference", text: "Kubernetes quantum biology" },
    ]);
    expect(profile.tools).not.toContain("kubernetes");
    expect(profile.domains).not.toContain("biology");
  });
});
