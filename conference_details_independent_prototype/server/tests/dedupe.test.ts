import { describe, expect, it } from "vitest";
import { dedupeEvents } from "../src/dedupe";
import type { EventItem } from "../src/types";

describe("dedupeEvents", () => {
  it("dedupes by normalized title, date, and url", () => {
    const base: EventItem = {
      id: "1",
      title: "Test Conference 2026",
      description: null,
      start: "2026-05-01T09:00:00.000Z",
      end: null,
      timezone: "UTC",
      source: "openalex",
      url: "https://example.org/conf",
      cfp_deadline: null,
      tags: ["AI"],
      fetched_at: "2026-01-01T00:00:00.000Z",
    };
    const dup: EventItem = {
      ...base,
      id: "2",
      title: "Test Conference 2026!",
      source: "crossref",
      description: "More detail",
      url: "http://example.org/conf/",
    };

    const result = dedupeEvents([base, dup]);
    expect(result).toHaveLength(1);
    expect(result[0].description).toBe("More detail");
  });
});
