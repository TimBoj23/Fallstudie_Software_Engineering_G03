import { useEffect, useMemo, useState } from "react";
import AppShell from "./components/AppShell.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Rooms from "./pages/Rooms.jsx";
import Assets from "./pages/Assets.jsx";
import MyBookings from "./pages/MyBookings.jsx";
import CreateBooking from "./pages/CreateBooking.jsx";
import Availability from "./pages/Availability.jsx";
import Admin from "./pages/Admin.jsx";
import JoinBooking from "./pages/JoinBooking.jsx";
import { clearAuthState, loadAuthState, saveAuthState } from "./state/authStore.js";
import { applyTheme, loadTheme } from "./state/themeStore.js";
import { logoutUser } from "./api/authApi.js";
import { getFavorites, setFavorite } from "./api/usersApi.js";
import QrCheckIn from "./pages/QrCheckIn.jsx";
import Settings from "./pages/Settings.jsx";
import Notifications from "./pages/Notifications.jsx";

export default function App() {
  const initialAuth = useMemo(() => loadAuthState(), []);
  const initialCheckInToken = useMemo(() => new URLSearchParams(window.location.search).get("checkin") || "", []);
  const initialInvitationCode = useMemo(() => new URLSearchParams(window.location.search).get("invite") || "", []);
  const [page, setPage] = useState(initialCheckInToken ? "qrCheckIn" : initialInvitationCode ? "joinBooking" : "dashboard");
  const [auth, setAuth] = useState(initialAuth);
  const [bookingDefaults, setBookingDefaults] = useState({});
  const [theme, setTheme] = useState(loadTheme);
  const [favorites, setFavorites] = useState([]);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const isLoggedIn = Boolean(auth.token && auth.user);
  const isAdmin = auth.user?.role === "admin";

  useEffect(() => {
    if (!isLoggedIn) {
      setFavorites([]);
      return;
    }
    getFavorites()
      .then((result) => setFavorites(result.favorites || []))
      .catch(() => setFavorites([]));
  }, [isLoggedIn]);

  async function toggleFavorite(targetType, targetId) {
    const key = `${targetType}:${targetId}`;
    const enabled = !favorites.some((favorite) => favorite.key === key);
    const result = await setFavorite(targetType, targetId, enabled);
    setFavorites(result.favorites || []);
  }

  function handleLogin(token, user) {
    saveAuthState(token, user);
    setAuth({ token, user });
    setPage("dashboard");
  }

  async function handleLogout() {
    try {
      if (auth.token) {
        await logoutUser();
      }
    } catch {
      // Die aktuelle Sitzung wird im Browser gespeichert; Logout darf auch ohne Serverantwort wirken.
    }
    clearAuthState();
    setAuth({ token: null, user: null });
    setPage("dashboard");
  }

  function handleUserUpdated(user) {
    saveAuthState(auth.token, user);
    setAuth((current) => ({ ...current, user }));
  }

  function handleAccountDeleted() {
    clearAuthState();
    setAuth({ token: null, user: null });
    setFavorites([]);
    setPage("dashboard");
  }

  function navigate(pageId) {
    if (pageId === "createBooking") {
      setBookingDefaults({});
    }
    setPage(pageId);
  }

  function openCreateBooking(defaults) {
    setBookingDefaults(defaults || {});
    setPage("createBooking");
  }

  const pages = {
    dashboard: <Dashboard setPage={navigate} isLoggedIn={isLoggedIn} />,
    login: <Login onLogin={handleLogin} setPage={navigate} />,
    register: <Register setPage={navigate} />,
    rooms: <Rooms key="rooms" category="rooms" setPage={navigate} openCreateBooking={openCreateBooking} favorites={favorites} onToggleFavorite={isLoggedIn ? toggleFavorite : null} />,
    sharedOffices: <Rooms key="shared-offices" category="sharedOffices" setPage={navigate} openCreateBooking={openCreateBooking} favorites={favorites} onToggleFavorite={isLoggedIn ? toggleFavorite : null} />,
    assets: <Assets setPage={navigate} openCreateBooking={openCreateBooking} favorites={favorites} onToggleFavorite={isLoggedIn ? toggleFavorite : null} />,
    bookings: <MyBookings isLoggedIn={isLoggedIn} setPage={navigate} openCreateBooking={openCreateBooking} />,
    createBooking: <CreateBooking isLoggedIn={isLoggedIn} setPage={navigate} bookingDefaults={bookingDefaults} />,
    availability: <Availability />,
    joinBooking: <JoinBooking initialCode={initialInvitationCode} />,
    qrCheckIn: <QrCheckIn token={initialCheckInToken} isLoggedIn={isLoggedIn} setPage={navigate} />,
    admin: <Admin isAdmin={isAdmin} isLoggedIn={isLoggedIn} />,
    settings: (
      <Settings
        user={auth.user}
        isLoggedIn={isLoggedIn}
        setPage={navigate}
        onUserUpdated={handleUserUpdated}
        onAccountDeleted={handleAccountDeleted}
      />
    ),
    notifications: <Notifications isLoggedIn={isLoggedIn} user={auth.user} setPage={navigate} />,
  };

  return (
    <AppShell
      page={page}
      setPage={navigate}
      user={auth.user}
      isLoggedIn={isLoggedIn}
      isAdmin={isAdmin}
      onLogout={handleLogout}
      theme={theme}
      onToggleTheme={() => setTheme((current) => current === "dark" ? "light" : "dark")}
    >
      {pages[page] || pages.dashboard}
    </AppShell>
  );
}
