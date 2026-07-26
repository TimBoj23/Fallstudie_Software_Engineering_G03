import { LogIn, LogOut, Moon, Settings, Sun, UserRound } from "lucide-react";
import Button from "./Button.jsx";

export default function Header({ user, isLoggedIn, onLogout, setPage, theme, onToggleTheme }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">RePlan Workspace</p>
        <h1>Räume und Ressourcen buchen</h1>
      </div>
      <div className="topbar-actions">
        <Button
          variant="secondary"
          className="theme-toggle"
          icon={theme === "dark" ? Sun : Moon}
          onClick={onToggleTheme}
          aria-label={theme === "dark" ? "Hellen Modus einschalten" : "Dunklen Modus einschalten"}
          title={theme === "dark" ? "Heller Modus" : "Dunkler Modus"}
        >
          {theme === "dark" ? "Hell" : "Dunkel"}
        </Button>
        {isLoggedIn ? (
          <>
            <button className="user-pill user-pill-button" type="button" onClick={() => setPage("settings")} title="Kontoeinstellungen öffnen">
              <UserRound size={16} />
              <span>{user?.name || user?.email}</span>
              {user?.role === "admin" && <strong>Admin</strong>}
              <Settings size={15} />
            </button>
            <Button variant="secondary" icon={LogOut} onClick={onLogout}>
              Logout
            </Button>
          </>
        ) : (
          <Button icon={LogIn} onClick={() => setPage("login")}>
            Login
          </Button>
        )}
      </div>
    </header>
  );
}
