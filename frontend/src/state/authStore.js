export function loadAuthState() {
  const token = localStorage.getItem("replan_token");
  const userJson = localStorage.getItem("replan_user");
  return {
    token,
    user: userJson ? JSON.parse(userJson) : null,
  };
}

export function saveAuthState(token, user) {
  localStorage.setItem("replan_token", token);
  localStorage.setItem("replan_user", JSON.stringify(user));
}

export function clearAuthState() {
  localStorage.removeItem("replan_token");
  localStorage.removeItem("replan_user");
}
