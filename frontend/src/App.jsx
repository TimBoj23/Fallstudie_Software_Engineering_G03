import { useMemo, useState } from "react";
import AppShell from "./components/AppShell.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Rooms from "./pages/Rooms.jsx";
import Seats from "./pages/Seats.jsx";
import Assets from "./pages/Assets.jsx";
import MyBookings from "./pages/MyBookings.jsx";
import CreateBooking from "./pages/CreateBooking.jsx";
import Availability from "./pages/Availability.jsx";
import Admin from "./pages/Admin.jsx";
import { clearAuthState, loadAuthState, saveAuthState } from "./state/authStore.js";
import { logoutUser } from "./api/authApi.js";

export default function App() {
  const initialAuth = useMemo(() => loadAuthState(), []);
  const [page, setPage] = useState("dashboard");
  const [auth, setAuth] = useState(initialAuth);

  const isLoggedIn = Boolean(auth.token && auth.user);
  const isAdmin = auth.user?.role === "admin";

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

  const pages = {
    dashboard: <Dashboard setPage={setPage} isLoggedIn={isLoggedIn} />,
    login: <Login onLogin={handleLogin} setPage={setPage} />,
    register: <Register setPage={setPage} />,
    rooms: <Rooms setPage={setPage} />,
    seats: <Seats setPage={setPage} />,
    assets: <Assets setPage={setPage} />,
    bookings: <MyBookings isLoggedIn={isLoggedIn} setPage={setPage} />,
    createBooking: <CreateBooking isLoggedIn={isLoggedIn} setPage={setPage} />,
    availability: <Availability />,
    admin: <Admin isAdmin={isAdmin} isLoggedIn={isLoggedIn} />,
  };

  return (
    <AppShell
      page={page}
      setPage={setPage}
      user={auth.user}
      isLoggedIn={isLoggedIn}
      isAdmin={isAdmin}
      onLogout={handleLogout}
    >
      {pages[page] || pages.dashboard}
    </AppShell>
  );
}
