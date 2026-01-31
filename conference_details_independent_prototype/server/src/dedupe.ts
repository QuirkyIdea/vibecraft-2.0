import type { EventItem } from "./types";
import { buildEventKey } from "./normalize";

export const dedupeEvents = (events: EventItem[]) => {
  const map = new Map<string, EventItem>();
  events.forEach((event) => {
    const key = buildEventKey(event);
    if (!map.has(key)) {
      map.set(key, event);
      return;
    }
    const existing = map.get(key)!;
    if (event.description && !existing.description) {
      map.set(key, { ...existing, description: event.description });
    }
  });
  return Array.from(map.values());
};
