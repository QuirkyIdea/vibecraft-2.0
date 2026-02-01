export type Source = "openalex" | "crossref" | "eventbrite" | "wikicfp";

export interface EventItem {
  id: string;
  title: string;
  description: string | null;
  start: string;
  end: string | null;
  timezone: string;
  source: Source;
  url: string;
  cfp_deadline: string | null;
  tags: string[];
  fetched_at: string;
  venue?: string | null;
  region?: string | null;
}
