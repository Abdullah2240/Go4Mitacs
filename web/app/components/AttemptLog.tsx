import { PoolAttemptLog } from "../../lib/ai/providers";

const outcomeText: Record<PoolAttemptLog["outcome"], (label: string) => string> = {
  sending: (label) => `Sending request using key "${label}"...`,
  succeeded: (label) => `Key "${label}" succeeded.`,
  "rate-limited": (label) => `Key "${label}" hit its rate limit or quota - switching to the next key, no progress lost.`,
  failed: (label) => `Key "${label}" failed.`,
};

type Props = { entries: PoolAttemptLog[] };
export function AttemptLog({ entries }: Props) {
  if (!entries.length) return null;
  return <div className="attempt-log" role="log" aria-live="polite"><strong>Request log</strong><ul>{entries.map((entry, index) => <li key={index} className={`attempt-${entry.outcome}`}>{outcomeText[entry.outcome](entry.keyLabel)}</li>)}</ul></div>;
}
