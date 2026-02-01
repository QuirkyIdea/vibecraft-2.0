import type { EventItem } from "../types";
import { dateFromParts, normalizeDate } from "../normalize";

type CrossrefItem = {
  DOI?: string;
  title?: string[];
  URL?: string;
  subject?: string[];
  issued?: { "date-parts": number[][] };
  event?: {
    name?: string;
    location?: string;
    start?: { "date-parts": number[][] };
    end?: { "date-parts": number[][] };
  };
  "container-title"?: string[];
};

export const fetchCrossrefEvents = async (from: string, to: string) => {
  const url = new URL("https://api.crossref.org/works");
  url.searchParams.set(
    "filter",
    `type:proceedings,from-pub-date:${from},until-pub-date:${to}`
  );
  url.searchParams.set("rows", "50");

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Crossref fetch failed: ${response.statusText}`);
  }
  const payload = (await response.json()) as { message: { items: CrossrefItem[] } };
  const fetchedAt = new Date().toISOString();

  return payload.message.items.map<EventItem>((item) => {
    const startParts = item.event?.start?.["date-parts"]?.[0];
    const endParts = item.event?.end?.["date-parts"]?.[0];
    const issuedParts = item.issued?.["date-parts"]?.[0];
    const start =
      (startParts && dateFromParts(startParts)) ||
      (issuedParts && dateFromParts(issuedParts)) ||
      normalizeDate(from) ||
      fetchedAt;
    const end = endParts ? dateFromParts(endParts) : null;
    return {
      id: item.DOI ?? `${item.URL ?? "crossref"}-${start}`,
      title: item.title?.[0] ?? "Conference Proceedings",
      description: null,
      start,
      end,
      timezone: "UTC",
      source: "crossref",
      url: item.URL ?? "https://www.crossref.org",
      cfp_deadline: null,
      tags: item.subject?.slice(0, 4) ?? ["Conference"],
      fetched_at: fetchedAt,
      venue: item.event?.name ?? item["container-title"]?.[0] ?? null,
      region: item.event?.location ?? null,
    };
  });
};
