type AdminPanelProps = {
  status: Record<string, string | null>;
};

const AdminPanel = ({ status }: AdminPanelProps) => {
  const sources = Object.keys(status);
  return (
    <div className="space-y-4 p-2">
      <div>
        <h3 className="text-lg font-semibold text-ink-900">
          Fetch Status & Sources
        </h3>
        <p className="text-sm text-ink-500">
          Sources enabled for this session and their last fetch timestamps.
        </p>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {sources.length ? (
          sources.map((source) => (
            <div
              key={source}
              className="rounded-2xl border border-ink-100 bg-white p-4 shadow-card"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-400">
                {source}
              </p>
              <p className="text-sm text-ink-600">
                {status[source] ?? "Not fetched yet"}
              </p>
            </div>
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-ink-100 bg-ink-50 px-6 py-12 text-center text-sm text-ink-500">
            No status available. Trigger a refresh to populate data.
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
