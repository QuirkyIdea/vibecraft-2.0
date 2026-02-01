import { describe, expect, it } from "vitest";
import { dateFromParts, normalizeDate } from "../src/normalize";

describe("normalizeDate", () => {
  it("normalizes YYYY-MM-DD to ISO", () => {
    const normalized = normalizeDate("2026-04-01");
    expect(normalized).toMatch(/^2026-04-01T09:00:00\.000Z$/);
  });
});

describe("dateFromParts", () => {
  it("builds ISO from date parts", () => {
    const normalized = dateFromParts([2026, 7, 4]);
    expect(normalized).toMatch(/^2026-07-04T09:00:00\.000Z$/);
  });
});
