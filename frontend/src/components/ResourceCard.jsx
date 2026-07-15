import { CalendarPlus, MapPin, Users } from "lucide-react";
import Button from "./Button.jsx";

export default function ResourceCard({ title, meta, description, chips = [], onBook, capacity, location }) {
  return (
    <article className="resource-card">
      <div className="resource-card-main">
        <div>
          <h3>{title}</h3>
          {meta && <p className="resource-meta">{meta}</p>}
        </div>
      </div>
      {(location || capacity) && (
        <div className="resource-facts">
          {location && <span><MapPin size={14} />{location}</span>}
          {capacity && <span><Users size={14} />bis {capacity} Personen</span>}
        </div>
      )}
      {description && <p className="resource-description">{description}</p>}
      {chips.length > 0 && (
        <div className="chip-row">
          {chips.map((chip) => (
            <span className="chip" key={chip}>{chip}</span>
          ))}
        </div>
      )}
      <div className="resource-actions">
        {onBook && (
          <Button variant="primary" icon={CalendarPlus} onClick={onBook}>
            Reservieren
          </Button>
        )}
      </div>
    </article>
  );
}
