import { StepId, WorkspaceStep } from "./types";

type WorkspaceTabsProps = { active: StepId; steps: readonly WorkspaceStep[]; onChange: (step: StepId) => void };

export function WorkspaceTabs({ active, steps, onChange }: WorkspaceTabsProps) {
  return <nav className="workspace-tabs" aria-label="Workspace sections">{steps.map(([id, label]) => <button key={id} className={active === id ? "active" : ""} aria-current={active === id ? "page" : undefined} onClick={() => onChange(id)}>{label}</button>)}</nav>;
}
