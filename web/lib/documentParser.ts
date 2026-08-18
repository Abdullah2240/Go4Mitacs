import { DocumentRecord } from "./localMode";

const MAX_CHARS = 250_000;
const textLike = /\.(txt|md|csv|json|html?|py|js|jsx|ts|tsx|java|c|cpp|h|hpp|go|rs|rb|php|sql|yml|yaml|xml|toml|sh)$/i;
async function hashText(text: string) { const bytes = new TextEncoder().encode(text); const digest = await crypto.subtle.digest("SHA-256", bytes); return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join(""); }
function limit(text: string) { return text.length > MAX_CHARS ? `${text.slice(0, MAX_CHARS)}\n\n[Truncated at ${MAX_CHARS.toLocaleString()} characters]` : text; }

export async function parseDocument(file: File, kind: "candidate" | "reference" = "candidate"): Promise<DocumentRecord> {
  try {
    let text = "";
    if (textLike.test(file.name) || file.type.startsWith("text/")) text = await file.text();
    else if (file.name.toLowerCase().endsWith(".pdf")) {
      // @ts-ignore browser-only optional dependency
      const pdfjs = await import("pdfjs-dist/legacy/build/pdf.mjs");
      // PDF.js 4+ no longer supplies a usable browser worker URL by default.
      // Keep the worker external and version-pinned: bundling pdf.worker.mjs
      // through Next/Terser turns its ESM output into an invalid script.
      if (!pdfjs.GlobalWorkerOptions.workerSrc) {
        pdfjs.GlobalWorkerOptions.workerSrc =
          "https://unpkg.com/pdfjs-dist@6.2.108/legacy/build/pdf.worker.mjs";
      }
      const pdf = await pdfjs.getDocument({ data: await file.arrayBuffer() }).promise;
      const pages: string[] = []; for (let i = 1; i <= pdf.numPages; i += 1) { const page = await pdf.getPage(i); const content = await page.getTextContent(); pages.push(content.items.map((item: any) => item.str ?? "").join(" ")); }
      text = pages.join("\n\n");
    } else if (file.name.toLowerCase().endsWith(".docx")) {
      // @ts-ignore browser-only optional dependency
      const mammoth = await import("mammoth"); text = (await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() })).value;
    } else if (file.name.toLowerCase().endsWith(".xlsx")) {
      // @ts-ignore browser-only optional dependency
      const XLSX = await import("xlsx"); const workbook = XLSX.read(await file.arrayBuffer(), { type: "array" }); text = workbook.SheetNames.map((sheet: string) => `## ${sheet}\n${XLSX.utils.sheet_to_csv(workbook.Sheets[sheet])}`).join("\n\n");
    } else throw new Error("Unsupported format. Use TXT, Markdown, CSV, JSON, HTML, source text, PDF, DOCX, or XLSX.");
    text = limit(text.replace(/\u0000/g, "").trim());
    return { id: crypto.randomUUID(), name: file.name, type: file.type || file.name.split(".").pop()?.toUpperCase() || "FILE", chars: text.length, text, hash: await hashText(text), status: "ready", size: file.size, createdAt: new Date().toISOString(), kind };
  } catch (error) { return { id: crypto.randomUUID(), name: file.name, type: file.type || "FILE", chars: 0, text: "", hash: "", status: "error", error: error instanceof Error ? error.message : "Could not parse this file safely in the browser.", size: file.size, createdAt: new Date().toISOString(), kind }; }
}

export async function pasteDocument(text: string): Promise<DocumentRecord> { const value = limit(text.trim()); return { id: crypto.randomUUID(), name: `Pasted evidence ${new Date().toLocaleString()}`, type: "PASTE", chars: value.length, text: value, hash: await hashText(value), status: "ready", size: new Blob([value]).size, createdAt: new Date().toISOString() }; }
