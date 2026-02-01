import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { loadCache, getCache, isFresh, updateCache, updateLastFetch } from "./cache";
import type { EventItem, Source } from "./types";
import { dedupeEvents } from "./dedupe";
import { fetchOpenAlexEvents } from "./sources/openalex";
import { fetchCrossrefEvents } from "./sources/crossref";

dotenv.config();

const app = express();
const port = Number(process.env.PORT ?? 5175);
const allowedOrigins = process.env.CORS_ORIGIN?.split(",") ?? ["*"];
const adminToken = process.env.ADMIN_TOKEN;
const enableBackgroundFetch = process.env.ENABLE_BACKGROUND_FETCH !== "false";
const refreshIntervalMinutes = Number(process.env.REFRESH_INTERVAL_MINUTES ?? 60);

app.use(express.json());
app.use(
  cors({
    origin: allowedOrigins,
  })
);

loadCache();

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const withRetry = async <T>(fn: () => Promise<T>, retries = 2) => {
  try {
    return await fn();
  } catch (error) {
    if (retries <= 0) throw error;
    await sleep(400 * (3 - retries));
    return withRetry(fn, retries - 1);
  }
};

const sourceFetchers: Record<Source, (from: string, to: string) => Promise<EventItem[]>> =
  {
    openalex: fetchOpenAlexEvents,
    crossref: fetchCrossrefEvents,
    eventbrite: async () => [],
    wikicfp: async () => [],
  };

const parseSources = (value?: string) => {
  if (!value) return ["openalex", "crossref"] as Source[];
  return value
    .split(",")
    .map((source) => source.trim())
    .filter((source): source is Source =>
      ["openalex", "crossref", "eventbrite", "wikicfp"].includes(source)
    );
};

const isWithinRange = (event: EventItem, from: string, to: string) => {
  const start = new Date(event.start).getTime();
  const fromTime = new Date(from).getTime();
  const toTime = new Date(to).getTime();
  if (Number.isNaN(start) || Number.isNaN(fromTime) || Number.isNaN(toTime)) {
    return true;
  }
  return start >= fromTime && start <= toTime;
};

const refreshSources = async (sources: Source[], from: string, to: string, force = false) => {
  const cache = getCache();
  const sourcesToFetch = sources.filter(
    (source) => force || !isFresh(cache.lastFetch[source])
  );
  if (!sourcesToFetch.length) {
    return cache;
  }

  const fetchedAt = new Date().toISOString();
  const fetchedEvents: EventItem[] = [];

  for (const source of sourcesToFetch) {
    const events = await withRetry(() => sourceFetchers[source](from, to));
    fetchedEvents.push(...events);
    updateLastFetch(cache, source, fetchedAt);
  }

  const preserved = cache.events.filter(
    (event) => !sourcesToFetch.includes(event.source)
  );
  const merged = dedupeEvents([...preserved, ...fetchedEvents]);

  const updated: typeof cache = {
    ...cache,
    events: merged,
  };

  updateCache(updated);
  return updated;
};

app.get("/api/events", async (req, res) => {
  const from = String(req.query.from ?? "");
  const to = String(req.query.to ?? "");
  if (!from || !to) {
    return res.status(400).json({ message: "from/to are required" });
  }
  const sources = parseSources(String(req.query.source ?? ""));

  try {
    const cache = await refreshSources(sources, from, to);
    const filtered = cache.events.filter(
      (event) => sources.includes(event.source) && isWithinRange(event, from, to)
    );
    return res.json(filtered);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to fetch events";
    return res.status(502).json({ message });
  }
});

app.get("/api/event/:id", (req, res) => {
  const cache = getCache();
  const event = cache.events.find((item) => item.id === req.params.id);
  if (!event) {
    return res.status(404).json({ message: "Event not found" });
  }
  return res.json(event);
});

app.get("/api/admin/status", (req, res) => {
  const cache = getCache();
  return res.json(cache.lastFetch);
});

app.post("/api/admin/fetch-now", async (req, res) => {
  if (adminToken && req.headers["x-admin-token"] !== adminToken) {
    return res.status(403).json({ message: "Forbidden" });
  }
  const from = String(req.query.from ?? new Date().toISOString().slice(0, 10));
  const to = String(req.query.to ?? new Date().toISOString().slice(0, 10));
  const sources = ["openalex", "crossref"] as Source[];
  try {
    await refreshSources(sources, from, to, true);
    return res.json({ message: "Refresh complete" });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to refresh sources";
    return res.status(502).json({ message });
  }
});

if (enableBackgroundFetch) {
  setInterval(() => {
    const from = new Date().toISOString().slice(0, 10);
    const to = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
      .toISOString()
      .slice(0, 10);
    refreshSources(["openalex", "crossref"], from, to).catch((error) =>
      console.warn("Background fetch failed", error)
    );
  }, refreshIntervalMinutes * 60 * 1000);
}

app.listen(port, () => {
  console.log(`Conference API listening on port ${port}`);
});
