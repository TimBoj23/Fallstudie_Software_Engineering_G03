import { useEffect, useMemo, useState } from "react";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";
import { getBookingSchedule } from "../api/bookingsApi.js";
import Button from "./Button.jsx";
import LoadingState from "./LoadingState.jsx";
import Panel from "./Panel.jsx";
import StatusMessage from "./StatusMessage.jsx";

export default function ObjectCalendar({ target, onSelectBlock }) {
  const [startDate, setStartDate] = useState(todayIsoDate());
  const [selectedDate, setSelectedDate] = useState(todayIsoDate());
  const [state, setState] = useState({ loading: true, error: "", schedule: [] });

  useEffect(() => {
    if (!target?.id || !target?.targetType) return;
    let ignore = false;
    async function loadSchedule() {
      setState((current) => ({ ...current, loading: true, error: "" }));
      try {
        const data = await getBookingSchedule({
          target_id: target.id,
          target_type: target.targetType,
          start_date: startDate,
          days: 7,
        });
        if (!ignore) {
          const schedule = data.schedule || [];
          setState({ loading: false, error: "", schedule });
          if (!schedule.some((day) => day.date === selectedDate)) {
            setSelectedDate(schedule[0]?.date || startDate);
          }
        }
      } catch (error) {
        if (!ignore) {
          setState({ loading: false, error: error.message, schedule: [] });
        }
      }
    }
    loadSchedule();
    return () => {
      ignore = true;
    };
  }, [target?.id, target?.targetType, startDate]);

  const selectedDay = useMemo(
    () => state.schedule.find((day) => day.date === selectedDate) || state.schedule[0],
    [state.schedule, selectedDate],
  );

  function moveDays(days) {
    setStartDate(addDays(startDate, days));
  }

  return (
    <Panel
      title={`${target.name} Kalender`}
      caption={target.meta || "Zeitblöcke 08:00 bis 22:00 Uhr"}
      actions={(
        <div className="calendar-actions">
          <Button variant="secondary" icon={ChevronLeft} className="button-icon" aria-label="Vorherige Woche" onClick={() => moveDays(-7)} />
          <Button variant="secondary" icon={CalendarDays} onClick={() => setStartDate(todayIsoDate())}>Heute</Button>
          <Button variant="secondary" icon={ChevronRight} className="button-icon" aria-label="Nächste Woche" onClick={() => moveDays(7)} />
        </div>
      )}
    >
      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.loading ? <LoadingState label="Kalender wird geladen..." /> : (
        <div className="object-calendar">
          <div className="calendar-days">
            {state.schedule.map((day) => (
              <button
                key={day.date}
                type="button"
                className={`calendar-day ${day.status} ${day.date === selectedDay?.date ? "active" : ""}`}
                onClick={() => setSelectedDate(day.date)}
                aria-label={formatWeekday(day.date)}
              >
                <span>{formatWeekday(day.date)}</span>
                <strong>{formatDay(day.date)}</strong>
              </button>
            ))}
          </div>

          <div className="time-block-grid">
            {(selectedDay?.slots || []).map((slot) => (
              <button
                key={slot.start_time}
                type="button"
                className={`time-block ${slotStatus(slot)}`}
                disabled={!slot.available}
                onClick={() => onSelectBlock?.({
                  targetType: target.targetType,
                  targetId: target.id,
                  startTime: slot.start_time,
                  endTime: slot.end_time,
                  title: `${target.name} ${slot.label}`,
                })}
              >
                {slot.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}

export function slotStatus(slot) {
  if (slot.booked && !slot.available) return "booked-full";
  if (slot.booked) return "booked-partial";
  if (!slot.available) return "blocked";
  return "free";
}

function todayIsoDate() {
  const date = new Date();
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0"),
  ].join("-");
}

function addDays(value, days) {
  const date = new Date(`${value}T12:00:00`);
  date.setDate(date.getDate() + days);
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0"),
  ].join("-");
}

function formatWeekday(value) {
  return new Intl.DateTimeFormat("de-DE", { weekday: "short" }).format(new Date(`${value}T12:00:00`));
}

function formatDay(value) {
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(`${value}T12:00:00`));
}
