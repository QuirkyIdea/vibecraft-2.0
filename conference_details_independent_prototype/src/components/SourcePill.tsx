import type { Source } from "../types";

const sourceStyles: Record<Source, string> = {
  openalex: "bg-brand-50 text-brand-600",
  crossref: "bg-ink-50 text-ink-700",
  eventbrite: "bg-orange-50 text-orange-600",
  wikicfp: "bg-emerald-50 text-emerald-600",
};

const SourcePill = ({ source }: { source: Source }) => {
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.15em] ${sourceStyles[source]}`}
    >
      {source}
    </span>
  );
};

export default SourcePill;
