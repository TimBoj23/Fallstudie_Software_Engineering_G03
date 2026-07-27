import {
  Armchair,
  Bell,
  Boxes,
  Building2,
  CalendarCheck,
  ClipboardList,
  Gauge,
  PlusCircle,
  SearchCheck,
  Settings,
  ShieldCheck,
  UserRoundCheck,
} from "lucide-react";

const primaryItems = [
  { id: "dashboard", label: "Dashboard", icon: Gauge },
  { id: "rooms", label: "Räume", icon: Building2 },
  { id: "sharedOffices", label: "Shared Offices", icon: Armchair },
  { id: "assets", label: "Ausstattung", icon: Boxes },
  { id: "availability", label: "Verfügbarkeit", icon: SearchCheck },
  { id: "joinBooking", label: "Einladung annehmen", icon: UserRoundCheck },
];

const bookingItems = [
  { id: "bookings", label: "Meine Buchungen", icon: ClipboardList },
  { id: "createBooking", label: "Buchung erstellen", icon: PlusCircle },
];

const accountItems = [
  { id: "notifications", label: "Benachrichtigungen", icon: Bell },
  { id: "settings", label: "Einstellungen", icon: Settings },
];

export default function Sidebar({ activePage, setPage, isLoggedIn, isAdmin }) {
  return (
    <aside className="sidebar">
      <button className="brand" type="button" onClick={() => setPage("dashboard")}>
        <span className="brand-mark"><CalendarCheck size={22} /></span>
        <span>
          <strong>RePlan</strong>
          <small>Raum & Ressourcen</small>
        </span>
      </button>

      <nav className="nav-group" aria-label="Hauptnavigation">
        {primaryItems.map((item) => (
          <NavButton key={item.id} item={item} active={activePage === item.id} onClick={setPage} />
        ))}
      </nav>

      <nav className="nav-group" aria-label="Buchungen">
        <p className="nav-caption">Buchungen</p>
        {bookingItems.map((item) => (
          <NavButton
            key={item.id}
            item={item}
            active={activePage === item.id}
            onClick={setPage}
            disabled={!isLoggedIn}
          />
        ))}
      </nav>

      {isLoggedIn && (
        <nav className="nav-group" aria-label="Konto">
          <p className="nav-caption">Konto</p>
          {accountItems.map((item) => (
            <NavButton key={item.id} item={item} active={activePage === item.id} onClick={setPage} />
          ))}
        </nav>
      )}

      {isAdmin && (
        <nav className="nav-group" aria-label="Administration">
          <p className="nav-caption">Administration</p>
          <NavButton
            item={{ id: "admin", label: "Admin", icon: ShieldCheck }}
            active={activePage === "admin"}
            onClick={setPage}
          />
        </nav>
      )}

      <div className="sidebar-note">
        <CalendarCheck size={16} />
        <span>Alle Reservierungen werden automatisch auf Überschneidungen geprüft.</span>
      </div>
    </aside>
  );
}

function NavButton({ item, active, onClick, disabled = false }) {
  const Icon = item.icon;
  return (
    <button
      type="button"
      className={`nav-button ${active ? "is-active" : ""}`}
      onClick={() => onClick(item.id)}
      disabled={disabled}
      title={disabled ? "Login erforderlich" : item.label}
    >
      <Icon size={18} />
      <span>{item.label}</span>
    </button>
  );
}
