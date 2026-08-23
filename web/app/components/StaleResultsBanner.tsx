type Props = { onRerun: () => void };
export function StaleResultsBanner({ onRerun }: Props) {
  return <div className="stale-banner" role="status"><span>Your profile changed since these matches were built. Results below may be out of date.</span><button className="button secondary" onClick={onRerun}>Re-run matching</button></div>;
}
