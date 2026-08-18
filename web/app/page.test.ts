import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const source = readFileSync(join(process.cwd(), "app/page.tsx"), "utf8");
const evidenceSource = readFileSync(join(process.cwd(), "app/components/EvidenceWorkspace.tsx"), "utf8");
const matchSource = readFileSync(join(process.cwd(), "app/components/MatchResults.tsx"), "utf8");
const comparisonSource = readFileSync(join(process.cwd(), "app/components/ComparisonView.tsx"), "utf8");
const settingsSource = readFileSync(join(process.cwd(), "app/components/SettingsDialog.tsx"), "utf8");

describe("workspace redesign contracts", () => {
  it("keeps the four-step navigation and evidence-first labels", () => {
    expect(source).toContain("[\"knowledge\", \"Evidence\"]");
    expect(source).toContain("[\"profile\", \"Profile\"]");
    expect(source).toContain("[\"results\", \"Matches\"]");
    expect(source).toContain("[\"shortlist\", \"Shortlist\"]");
    expect(source).toContain("<EvidenceWorkspace");
    expect(evidenceSource).toContain("Drop evidence here or choose files");
    expect(evidenceSource).toContain("Paste text");
    expect(evidenceSource).toContain("Optional private context");
  });

  it("hides provider settings by default and labels live AI as unavailable", () => {
    expect(source).toContain('const [settingsOpen, setSettingsOpen] = useState(false)');
    expect(source).toContain("settingsOpen &&");
    expect(matchSource).toContain("AI reranking is coming soon");
    expect(settingsSource).toContain("sessionStorage");
    expect(source).toContain("No provider request has been made.");
  });

  it("caps comparison at four and provides accessible removal", () => {
    expect(source).toContain("current.length >= 4 ? current");
    expect(comparisonSource).toContain("Remove ");
    expect(comparisonSource).toContain("Compare selected projects");
  });
});
