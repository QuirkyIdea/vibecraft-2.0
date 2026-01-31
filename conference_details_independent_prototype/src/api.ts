import type { EventItem, Source } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

type FetchEventsParams = {
  from: string;
  to: string;
  sources: Source[];
};

type StatusResponse = Record<string, string | null>;

const formatDate = (value: Date) => value.toISOString().slice(0, 10);

const withDefaultRange = (params: FetchEventsParams) => {
  if (params.from && params.to) {
    return params;
  }
  const start = new Date();
  start.setDate(1);
  const end = new Date(start);
  end.setMonth(end.getMonth() + 1);
  end.setDate(0);
  return {
    ...params,
    from: params.from || formatDate(start),
    to: params.to || formatDate(end),
  };
};

const buildQuery = (params: FetchEventsParams) => {
  const safeParams = withDefaultRange(params);
  const search = new URLSearchParams();
  search.set("from", safeParams.from);
  search.set("to", safeParams.to);
  if (safeParams.sources?.length) {
    search.set("source", safeParams.sources.join(","));
  }
  return search.toString();
};

export const fetchEvents = async (params: FetchEventsParams) => {
  if (USE_MOCK) {
    const data = await import("./data/mockEvents.json");
    return (data.default as EventItem[]).filter((event) => {
      const start = new Date(event.start).getTime();
      const fromTime = new Date(params.from).getTime();
      const toTime = new Date(params.to).getTime();
      if (Number.isNaN(start) || Number.isNaN(fromTime) || Number.isNaN(toTime)) {
        return true;
      }
      return start >= fromTime && start <= toTime;
    });
  }
  const url = `${API_BASE}/api/events?${buildQuery(params)}`;
  const response = await fetch(url);
  if (!response.ok) {
    console.error("Events fetch failed", { url, status: response.status });
    throw new Error("Failed to fetch events. Please try again.");
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    const body = await response.text();
    console.error("Expected JSON but received non-JSON response", {
      url,
      contentType,
      preview: body.slice(0, 200),
    });
    throw new Error("Events API returned an unexpected response.");
  }
  return (await response.json()) as EventItem[];
};

export const fetchStatus = async (): Promise<StatusResponse> => {
  if (USE_MOCK) {
    return {
      openalex: new Date().toISOString(),
      crossref: new Date().toISOString(),
      eventbrite: null,
      wikicfp: null,
    };
  }
  const response = await fetch(`${API_BASE}/api/admin/status`);
  if (!response.ok) {
    throw new Error("Failed to load admin status.");
  }
  return (await response.json()) as StatusResponse;
};

export const fetchNow = async () => {
  if (USE_MOCK) {
    return true;
  }
  const response = await fetch(`${API_BASE}/api/admin/fetch-now`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Unable to refresh right now.");
  }
  return true;
};
