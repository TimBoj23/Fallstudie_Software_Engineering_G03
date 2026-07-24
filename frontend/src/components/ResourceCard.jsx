import { CalendarDays, CalendarPlus, MapPin, Users } from "lucide-react";
import { mediaUrl } from "../api/client.js";
import Button from "./Button.jsx";

export default function ResourceCard({ title, meta, description, chips = [], onBook, onViewCalendar, capacity, location, imageUrl, available }) {
  return (
    <article className={`resource-card ${onViewCalendar ? "is-clickable" : ""}`} onClick={onViewCalendar}>
      {imageUrl && (
        <img className="resource-image" src={mediaUrl(imageUrl)} alt={title} loading="lazy" />
      )}
      <div className="resource-card-main">
        <div>
          <h3>{title}</h3>
          {meta && <p className="resource-meta">{meta}</p>}
        </div>
        {available !== undefined && (
          <span className={`availability-badge ${available ? "available" : "occupied"}`}>
            {available ? "buchbar" : "belegt"}
          </span>
        )}
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
        {onViewCalendar && (
          <Button
            variant="secondary"
            icon={CalendarDays}
            onClick={(event) => {
              event.stopPropagation();
              onViewCalendar();
            }}
          >
            Kalender
          </Button>
        )}
        {onBook && (
          <Button
            variant="primary"
            icon={CalendarPlus}
            onClick={(event) => {
              event.stopPropagation();
              onBook();
            }}
          >
            Reservieren
          </Button>
        )}
      </div>
    </article>
  );
}
