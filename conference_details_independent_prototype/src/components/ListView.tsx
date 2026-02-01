import { DateTime } from "luxon";
import type { EventItem } from "../types";
import SourcePill from "./SourcePill";

type ListViewProps = {
  events: EventItem[];
  timezone: string;
  onSelect: (event: EventItem) => void;
};

const formatRange = (event: EventItem, timezone: string) => {
  const start = DateTime.fromISO(event.start, { setZone: true }).setZone(timezone);
  const end = event.end
    ? DateTime.fromISO(event.end, { setZone: true }).setZone(timezone)
    : null;
  if (!end) {
    return start.toFormat("dd LLL yyyy, t ZZZZ");
  }
  return `${start.toFormat("dd LLL yyyy")} — ${end.toFormat("dd LLL yyyy")}`;
};

const ListView = ({ events, timezone, onSelect }: ListViewProps) => {
  if (!events.length) {
    return (
      <div className="rounded-2xl border border-dashed border-ink-100 bg-ink-50 px-6 py-12 text-center text-sm text-ink-500">
        No events match the current filters. Try expanding the date range or
        filters.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <button
          key={event.id}
          onClick={() => onSelect(event)}
          className="flex w-full flex-col gap-3 rounded-2xl border border-ink-100 bg-white p-4 text-left shadow-card transition hover:-translate-y-0.5 hover:border-brand-200"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-500">
                {formatRange(event, timezone)}
              </p>
              <h3 className="text-lg font-semibold text-ink-900">{event.title}</h3>
              {event.venue ? (
                <p className="text-sm text-ink-500">{event.venue}</p>
              ) : null}
            </div>
            <SourcePill source={event.source} />
          </div>
          <div className="flex flex-wrap gap-2">
            {event.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-ink-50 px-3 py-1 text-xs font-semibold text-ink-600"
              >
                {tag}
              </span>
            ))}
            {event.cfp_deadline ? (
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-600">
                CFP: {DateTime.fromISO(event.cfp_deadline).toFormat("dd LLL yyyy")}
              </span>
            ) : null}
          </div>
        </button>
      ))}
    </div>
  );
};

export default ListView;
