// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { getFocusableElements } from "./useFocusTrap";

describe("getFocusableElements", () => {
  it("finds buttons, inputs, links, and selects, skipping disabled ones", () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <button>A</button>
      <button disabled>B</button>
      <input type="text" />
      <a href="#">Link</a>
      <select><option>x</option></select>
      <div tabindex="-1">Not focusable by default</div>
    `;
    const found = getFocusableElements(container);
    expect(found.length).toBe(4);
  });

  it("returns an empty array for a container with no focusable children", () => {
    const container = document.createElement("div");
    container.innerHTML = "<p>Just text</p>";
    expect(getFocusableElements(container)).toEqual([]);
  });
});
