import clsx from "clsx";

export type FiltersState = {
  query: string;
  source: string;
  tag: string;
  region: string;
  deadline: string;
};

type FiltersBarProps = {
  filters: FiltersState;
  onChange: (filters: FiltersState) => void;
  sources: string[];
  tags: string[];
  regions: string[];
};

const FiltersBar = ({ filters, onChange, sources, tags, regions }: FiltersBarProps) => {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-card">
      <div className="grid gap-3 md:grid-cols-3">
        <input
          className="rounded-xl border border-ink-100 bg-ink-50 px-3 py-2 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
          placeholder="Search title or tags"
          value={filters.query}
          onChange={(event) => onChange({ ...filters, query: event.target.value })}
          aria-label="Search conferences"
        />
        <select
          className="rounded-xl border border-ink-100 bg-ink-50 px-3 py-2 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
          value={filters.source}
          onChange={(event) => onChange({ ...filters, source: event.target.value })}
          aria-label="Filter by source"
        >
          {sources.map((source) => (
            <option key={source} value={source}>
              {source === "all" ? "All sources" : source}
            </option>
          ))}
        </select>
        <select
          className={clsx(
            "rounded-xl border border-ink-100 bg-ink-50 px-3 py-2 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100",
            filters.tag === "all" ? "text-ink-500" : "text-ink-900"
          )}
          value={filters.tag}
          onChange={(event) => onChange({ ...filters, tag: event.target.value })}
          aria-label="Filter by topic"
        >
          {tags.map((tag) => (
            <option key={tag} value={tag}>
              {tag === "all" ? "All topics" : tag}
            </option>
          ))}
        </select>
        <select
          className="rounded-xl border border-ink-100 bg-ink-50 px-3 py-2 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
          value={filters.region}
          onChange={(event) => onChange({ ...filters, region: event.target.value })}
          aria-label="Filter by region"
        >
          {regions.map((region) => (
            <option key={region} value={region}>
              {region === "all" ? "All regions" : region}
            </option>
          ))}
        </select>
        <select
          className="rounded-xl border border-ink-100 bg-ink-50 px-3 py-2 text-sm focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-100"
          value={filters.deadline}
          onChange={(event) => onChange({ ...filters, deadline: event.target.value })}
          aria-label="Filter by CFP deadline"
        >
          <option value="any">Any deadline</option>
          <option value="30">Deadline in 30 days</option>
          <option value="60">Deadline in 60 days</option>
          <option value="90">Deadline in 90 days</option>
        </select>
      </div>
    </div>
  );
};

export default FiltersBar;
