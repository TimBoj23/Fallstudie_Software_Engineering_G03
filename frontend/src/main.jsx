import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { applyTheme, loadTheme } from "./state/themeStore.js";
import "./styles/theme.css";
import "./styles/global.css";
import "./styles/layout.css";
import "./styles/components.css";

applyTheme(loadTheme());

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
