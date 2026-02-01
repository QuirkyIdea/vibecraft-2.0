import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import type { EventItem } from "../types";

type CalendarViewProps = {
  events: EventItem[];
  onSelect: (event: EventItem) => void;
  onRangeChange?: (range: { from: string; to: string }) => void;
};

const CalendarView = ({ events, onSelect, onRangeChange }: CalendarViewProps) => {
  return (
    <FullCalendar
      plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
      initialView="dayGridMonth"
      headerToolbar={{
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
      }}
      height="auto"
      events={events.map((event) => ({
        id: event.id,
        title: event.title,
        start: event.start,
        end: event.end ?? undefined,
        extendedProps: event,
      }))}
      eventClick={(info) => onSelect(info.event.extendedProps as EventItem)}
      datesSet={(info) => {
        const from = info.startStr.slice(0, 10);
        const to = info.endStr.slice(0, 10);
        onRangeChange?.({ from, to });
      }}
      eventDidMount={(info) => {
        info.el.setAttribute("aria-label", info.event.title);
      }}
      nowIndicator
    />
  );
};

export default CalendarView;
