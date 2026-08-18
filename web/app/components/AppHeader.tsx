type AppHeaderProps = { onSettings: () => void; onClear: () => void };

export function AppHeader({ onSettings, onClear }: AppHeaderProps) {
  return <header className="masthead"><div className="masthead-brand"><span className="wordmark">Go4Mitacs</span><span className="masthead-divider" aria-hidden="true" /><span className="masthead-description">Independent project matching workspace</span></div><div className="masthead-actions"><span><strong>3,359</strong> public projects</span><span className="account-note">No account required</span><button className="text-action" onClick={onSettings}>Settings</button><button className="button ghost" onClick={onClear}>Clear workspace</button></div></header>;
}
