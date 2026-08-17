import { NextResponse } from "next/server";
import { publicCorpus } from "../../../lib/publicCorpus";

export function GET() { return NextResponse.json({ status: "ok", mode: "local-only", corpus_version: publicCorpus.corpus_version, corpus_count: publicCorpus.count }, { headers: { "Cache-Control": "public, max-age=60" } }); }
