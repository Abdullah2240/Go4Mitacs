import { LocalShortlistItem } from "../../lib/localMode";
import { ComparisonView } from "./ComparisonView";
import { Project } from "./types";

type Props = { shortlist: LocalShortlistItem[]; projects: Project[]; selected: string[]; onRemoveCompare: (id: string) => void; onExport: () => void; onBack: () => void };

export function ShortlistWorkspace({ shortlist, projects, selected, onRemoveCompare, onExport, onBack }: Props) {
  return <section className="stage"><div className="section-head compact"><div><p className="eyebrow">Shortlist</p><h1>Turn good matches into a plan.</h1><p>{shortlist.length} saved locally. Compare up to four projects and export when ready.</p></div><button className="button secondary" onClick={onExport}>Export Markdown</button></div>{shortlist.length === 0 ? <div className="empty large"><strong>Your shortlist is empty.</strong><span>Save projects from Matches to bring them here.</span><button className="button secondary" onClick={onBack}>Back to Matches</button></div> : <div className="shortlist-list">{shortlist.map((item) => <div className="short-row" key={item.project_id}><span className="rank">{String(item.rank).padStart(2, "0")}</span><div><h2>{item.title}</h2><p className="fine">Project {item.project_id}</p></div><span className={`tag ${item.classification}`}>{item.classification}</span></div>)}</div>}<ComparisonView selected={selected} projects={projects} onRemove={onRemoveCompare} /></section>;
}
