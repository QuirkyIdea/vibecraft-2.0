import { useEffect, useMemo, useState } from "react";
import { DateTime } from "luxon";
import { fetchEvents, fetchNow, fetchStatus } from "./api";
import type { EventItem, Source } from "./types";
import CalendarView from "./components/CalendarView";
import FiltersBar from "./components/FiltersBar";
import type { FiltersState } from "./components/FiltersBar";
import ListView from "./components/ListView";
import EventModal from "./components/EventModal";
import AdminPanel from "./components/AdminPanel";
import { motion } from "framer-motion";

const DEFAULT_TIMEZONE = "Asia/Kolkata";
const SOURCE_OPTIONS: Source[] = ["openalex", "crossref", "eventbrite", "wikicfp"];

const buildDateRange = () => {
  const start = DateTime.now().startOf("month");
  const end = start.plus({ months: 3 }).endOf("month");
  return {
    from: start.toISODate(),
    to: end.toISODate(),
  };
};

function App() {
  const [view, setView] = useState<"calendar" | "list" | "admin">("calendar");
  const [events, setEvents] = useState<EventItem[]>([]);
  const [status, setStatus] = useState<Record<string, string | null>>({});
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [range, setRange] = useState<{ from: string; to: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FiltersState>({
    query: "",
    source: "all",
    tag: "all",
    region: "all",
    deadline: "any",
  });
  const [timezoneMode, setTimezoneMode] = useState<"auto" | "manual">("auto");
  const [manualTimezone, setManualTimezone] = useState(DEFAULT_TIMEZONE);

  const detectedTimezone =
    Intl.DateTimeFormat().resolvedOptions().timeZone || DEFAULT_TIMEZONE;
  const activeTimezone =
    timezoneMode === "auto" ? detectedTimezone : manualTimezone;

  const refreshData = async (isManual = false, overrideRange?: { from: string; to: string }) => {
    const fallbackRange = buildDateRange();
    const activeRange = overrideRange ?? range ?? fallbackRange;
    setLoading(true);
    setError(null);
    try {
      if (isManual) {
        await fetchNow();
      }
      const response = await fetchEvents({
        from: activeRange.from,
        to: activeRange.to,
        sources: SOURCE_OPTIONS,
      });
      setEvents(response);
      try {
        const statusResponse = await fetchStatus();
        setStatus(statusResponse);
      } catch (statusError) {
        console.warn("Failed to load admin status", statusError);
      }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to load events right now.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const availableTags = useMemo(() => {
    const tags = new Set<string>();
    events.forEach((event) => {
      event.tags?.forEach((tag) => tags.add(tag));
    });
    return ["all", ...Array.from(tags).sort()];
  }, [events]);

  const availableRegions = useMemo(() => {
    const regions = new Set<string>();
    events.forEach((event) => {
      if (event.region) {
        regions.add(event.region);
      }
    });
    return ["all", ...Array.from(regions).sort()];
  }, [events]);

  const filteredEvents = useMemo(() => {
    const query = filters.query.trim().toLowerCase();
    return events.filter((event) => {
      const matchesQuery =
        !query ||
        event.title.toLowerCase().includes(query) ||
        event.tags.some((tag) => tag.toLowerCase().includes(query));
      const matchesSource =
        filters.source === "all" || event.source === filters.source;
      const matchesTag =
        filters.tag === "all" || event.tags.includes(filters.tag);
      const matchesRegion =
        filters.region === "all" || event.region === filters.region;
      const matchesDeadline =
        filters.deadline === "any" ||
        (event.cfp_deadline &&
          (() => {
            const daysLeft = DateTime.fromISO(event.cfp_deadline, {
              setZone: true,
            }).diffNow("days").days;
            return daysLeft >= 0 && daysLeft <= Number(filters.deadline);
          })());
      return (
        matchesQuery &&
        matchesSource &&
        matchesTag &&
        matchesRegion &&
        matchesDeadline
      );
    });
  }, [events, filters]);

  return (
    <div className="min-h-screen px-6 py-10 text-ink-900">
      <div className="mx-auto max-w-6xl space-y-10">
        <header className="flex flex-wrap items-start justify-between gap-6">
          <div className="max-w-2xl space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brand-600">
              Research Conference Calendar
            </p>
            <h1 className="text-3xl font-semibold text-ink-900">
              Global Conference Atlas
            </h1>
            <p className="text-sm text-ink-500">
              Aggregated academic events with CFP deadlines, sources, and smart
              filters.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-2xl bg-ink-50 px-4 py-3">
              <label className="text-[0.7rem] font-semibold uppercase tracking-[0.2em] text-ink-500">
                Timezone
              </label>
              <div className="mt-2 flex items-center gap-2">
                <select
                  className="rounded-lg border border-ink-100 bg-white px-2 py-1 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  value={timezoneMode}
                  onChange={(event) =>
                    setTimezoneMode(event.target.value as "auto" | "manual")
                  }
                  aria-label="Timezone mode"
                >
                  <option value="auto">Auto</option>
                  <option value="manual">Manual</option>
                </select>
                {timezoneMode === "manual" ? (
                  <input
                    className="w-40 rounded-lg border border-ink-100 bg-white px-2 py-1 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
                    value={manualTimezone}
                    onChange={(event) => setManualTimezone(event.target.value)}
                    aria-label="Manual timezone"
                  />
                ) : (
                  <span className="text-xs text-ink-500">{detectedTimezone}</span>
                )}
              </div>
            </div>
            <button
              onClick={() => refreshData(true)}
              className="rounded-xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-brand-500 active:translate-y-[1px]"
            >
              Refresh
            </button>
          </div>
        </header>

        <div className="flex flex-wrap items-center gap-2">
          {(["calendar", "list", "admin"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setView(tab)}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                view === tab
                  ? "bg-brand-600 text-white shadow-soft"
                  : "bg-ink-50 text-ink-500 hover:text-ink-800"
              }`}
              aria-pressed={view === tab}
            >
              {tab === "calendar" ? "Calendar" : tab === "list" ? "List" : "Admin"}
            </button>
          ))}
        </div>

        {error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {view !== "admin" && (
          <FiltersBar
            filters={filters}
            onChange={setFilters}
            sources={["all", ...SOURCE_OPTIONS]}
            tags={availableTags}
            regions={availableRegions}
          />
        )}

        {loading ? (
          <div className="rounded-2xl bg-white px-6 py-12 text-center shadow-card">
            <p className="text-sm text-ink-500">Fetching fresh events…</p>
          </div>
        ) : (
          <motion.div
            layout
            className="rounded-2xl border border-ink-100 bg-white/70 p-4 shadow-card"
          >
            {view === "calendar" ? (
              <CalendarView
                events={filteredEvents}
                onSelect={setSelectedEvent}
                onRangeChange={(nextRange) => {
                  setRange(nextRange);
                  refreshData(false, nextRange);
                }}
              />
            ) : view === "list" ? (
              <ListView
                events={filteredEvents}
                onSelect={setSelectedEvent}
                timezone={activeTimezone}
              />
            ) : (
              <AdminPanel status={status} />
            )}
          </motion.div>
        )}
      </div>

      <EventModal
        event={selectedEvent}
        timezone={activeTimezone}
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
}

export default App;
