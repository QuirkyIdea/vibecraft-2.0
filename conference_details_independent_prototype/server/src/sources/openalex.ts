import type { EventItem } from "../types";
import { normalizeDate } from "../normalize";

type OpenAlexWork = {
  id: string;
  display_name: string;
  publication_date?: string;
  primary_location?: {
    landing_page_url?: string;
    source?: {
      display_name?: string;
    };
  };
  concepts?: Array<{ display_name: string }>;
};

export const fetchOpenAlexEvents = async (from: string, to: string) => {
  const email = process.env.OPENALEX_EMAIL;
  const url = new URL("https://api.openalex.org/works");
  url.searchParams.set(
    "filter",
    `type:proceedings,from_publication_date:${from},to_publication_date:${to}`
  );
  url.searchParams.set("per-page", "50");
  if (email) {
    url.searchParams.set("mailto", email);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`OpenAlex fetch failed: ${response.statusText}`);
  }
  const payload = (await response.json()) as { results: OpenAlexWork[] };
  const fetchedAt = new Date().toISOString();

  return payload.results.map<EventItem>((work) => ({
    id: work.id,
    title: work.display_name,
    description: null,
    start: normalizeDate(work.publication_date) ?? fetchedAt,
    end: null,
    timezone: "UTC",
    source: "openalex",
    url: work.primary_location?.landing_page_url ?? work.id,
    cfp_deadline: null,
    tags: work.concepts?.slice(0, 4).map((concept) => concept.display_name) ?? [
      "Research",
    ],
    fetched_at: fetchedAt,
    venue: work.primary_location?.source?.display_name ?? null,
    region: null,
  }));
};
