import fs from "node:fs";
import path from "node:path";
import NodeCache from "node-cache";
import type { CacheData, Source } from "./types";

const CACHE_TTL_SECONDS = 60 * 60 * 12;
const CACHE_KEY = "events";
const CACHE_PATH = path.join(process.cwd(), "cache", "events.json");

const cache = new NodeCache({ stdTTL: CACHE_TTL_SECONDS });

const emptyCache = (): CacheData => ({
  events: [],
  lastFetch: {
    openalex: null,
    crossref: null,
    eventbrite: null,
    wikicfp: null,
  },
});

export const loadCache = () => {
  try {
    if (fs.existsSync(CACHE_PATH)) {
      const data = JSON.parse(fs.readFileSync(CACHE_PATH, "utf-8"));
      cache.set(CACHE_KEY, data);
      return data as CacheData;
    }
  } catch (error) {
    console.warn("Failed to read cache file", error);
  }
  const data = emptyCache();
  cache.set(CACHE_KEY, data);
  return data;
};

export const getCache = () => {
  const cached = cache.get<CacheData>(CACHE_KEY);
  if (cached) {
    return cached;
  }
  return loadCache();
};

export const updateCache = (data: CacheData) => {
  cache.set(CACHE_KEY, data);
  const dir = path.dirname(CACHE_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(CACHE_PATH, JSON.stringify(data, null, 2));
};

export const isFresh = (timestamp: string | null) => {
  if (!timestamp) return false;
  const lastFetch = new Date(timestamp).getTime();
  if (Number.isNaN(lastFetch)) return false;
  return Date.now() - lastFetch < CACHE_TTL_SECONDS * 1000;
};

export const updateLastFetch = (data: CacheData, source: Source, time: string) => {
  data.lastFetch[source] = time;
};
