import type { EventItem } from "./types";

export const normalizeTitle = (title: string) =>
  title.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

export const normalizeUrl = (rawUrl: string) => {
  try {
    const url = new URL(rawUrl);
    return `${url.hostname}${url.pathname}`.replace(/\/$/, "");
  } catch {
    return rawUrl.toLowerCase();
  }
};

export const dateFromParts = (parts: number[]) => {
  const [year, month = 1, day = 1] = parts;
  return new Date(Date.UTC(year, month - 1, day, 9, 0, 0)).toISOString();
};

export const normalizeDate = (date?: string | null) => {
  if (!date) return null;
  const iso = new Date(`${date}T09:00:00Z`);
  if (Number.isNaN(iso.getTime())) {
    return null;
  }
  return iso.toISOString();
};

export const buildEventKey = (event: EventItem) => {
  const dateKey = event.start ? event.start.slice(0, 10) : "unknown";
  return `${normalizeTitle(event.title)}|${dateKey}|${normalizeUrl(event.url)}`;
};
