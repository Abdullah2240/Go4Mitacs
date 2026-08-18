import { NextResponse } from "next/server";
import { GLOBALINK_PORTAL_URL, publicCorpus } from "../../../../lib/publicCorpus";

export function GET(_request: Request, context: { params: { projectId: string } }) { const project = publicCorpus.projects.find((item) => item.id === context.params.projectId); if (!project) return NextResponse.json({ detail: "project not found" }, { status: 404, headers: { "Cache-Control": "public, max-age=60" } }); return NextResponse.json({ ...project, source_url: GLOBALINK_PORTAL_URL }, { headers: { "Cache-Control": "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400" } }); }
