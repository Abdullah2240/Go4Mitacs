import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const source = readFileSync(join(process.cwd(), "app/page.tsx"), "utf8");

describe("workspace redesign contracts", () => {
  it("keeps the four-step navigation and evidence-first labels", () => {
    expect(source).toContain("[\"knowledge\", \"Evidence\"]");
    expect(source).toContain("[\"profile\", \"Profile\"]");
    expect(source).toContain("[\"results\", \"Matches\"]");
    expect(source).toContain("[\"shortlist\", \"Shortlist\"]");
    expect(source).toContain("Drop evidence here or choose files");
    expect(source).toContain("Paste text instead");
    expect(source).toContain("Optional private context");
  });

  it("hides provider settings by default and labels live AI as unavailable", () => {
    expect(source).toContain('const [settingsOpen, setSettingsOpen] = useState(false)');
    expect(source).toContain("settingsOpen &&");
    expect(source).toContain("AI reranking is coming soon");
    expect(source).toContain("No provider request has been made.");
  });

  it("caps comparison at four and provides accessible removal", () => {
    expect(source).toContain("current.length >= 4 ? current");
    expect(source).toContain("Remove ${p?.title ?? id} from comparison");
    expect(source).toContain("Compare selected projects");
  });
});
