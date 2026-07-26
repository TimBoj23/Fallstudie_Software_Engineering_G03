import { CalendarDays, CalendarPlus, Heart, MapPin, Users } from "lucide-react";
import { mediaUrl } from "../api/client.js";
import Button from "./Button.jsx";

export default function ResourceCard({ title, meta, description, chips = [], onBook, onViewCalendar, onToggleFavorite, favorite = false, capacity, location, imageUrl, imageFit = "cover", available }) {
  return (
    <article className={`resource-card ${onViewCalendar ? "is-clickable" : ""}`} onClick={onViewCalendar}>
      {imageUrl && (
        <img
          className={`resource-image ${imageFit === "contain" ? "resource-image-contain" : ""}`}
          src={mediaUrl(imageUrl)}
          alt={title}
          loading="lazy"
        />
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
        {onToggleFavorite && (
          <button
            type="button"
            className={`favorite-button ${favorite ? "active" : ""}`}
            aria-label={favorite ? "Aus Favoriten entfernen" : "Zu Favoriten hinzufügen"}
            title={favorite ? "Aus Favoriten entfernen" : "Zu Favoriten hinzufügen"}
            onClick={(event) => { event.stopPropagation(); onToggleFavorite(); }}
          >
            <Heart size={18} fill={favorite ? "currentColor" : "none"} />
          </button>
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
