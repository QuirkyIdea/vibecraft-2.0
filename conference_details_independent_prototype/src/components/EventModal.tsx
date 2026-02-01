import { DateTime } from "luxon";
import { AnimatePresence, motion } from "framer-motion";
import type { EventItem } from "../types";
import SourcePill from "./SourcePill";

type EventModalProps = {
  event: EventItem | null;
  timezone: string;
  onClose: () => void;
};

const EventModal = ({ event, timezone, onClose }: EventModalProps) => {
  if (!event) {
    return null;
  }

  const start = DateTime.fromISO(event.start, { setZone: true }).setZone(timezone);
  const end = event.end
    ? DateTime.fromISO(event.end, { setZone: true }).setZone(timezone)
    : null;
  const range = end
    ? `${start.toFormat("dd LLL yyyy")} — ${end.toFormat("dd LLL yyyy")}`
    : start.toFormat("dd LLL yyyy, t ZZZZ");

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        aria-modal="true"
        role="dialog"
      >
        <motion.div
          className="max-w-2xl rounded-2xl bg-white p-6 shadow-soft"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 20, opacity: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
          onClick={(event) => event.stopPropagation()}
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-500">
                {range}
              </p>
              <h2 className="text-2xl font-semibold text-ink-900">{event.title}</h2>
              {event.venue ? (
                <p className="text-sm text-ink-500">{event.venue}</p>
              ) : null}
            </div>
            <SourcePill source={event.source} />
          </div>

          <div className="mt-4 space-y-3 text-sm text-ink-600">
            {event.description ? <p>{event.description}</p> : null}
            <div className="flex flex-wrap gap-2">
              {event.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-ink-50 px-3 py-1 text-xs font-semibold text-ink-600"
                >
                  {tag}
                </span>
              ))}
            </div>
            <div className="grid gap-2 md:grid-cols-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-400">
                  Timezone
                </p>
                <p>{timezone}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-400">
                  CFP Deadline
                </p>
                <p>
                  {event.cfp_deadline
                    ? DateTime.fromISO(event.cfp_deadline).toFormat("dd LLL yyyy")
                    : "Not provided"}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-400">
                  Source Link
                </p>
                <a
                  href={event.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-600 underline"
                >
                  View original page
                </a>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-400">
                  Fetched At
                </p>
                <p>{DateTime.fromISO(event.fetched_at).toFormat("dd LLL yyyy")}</p>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="rounded-full bg-ink-900 px-4 py-2 text-sm font-semibold text-white"
            >
              Close
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default EventModal;
