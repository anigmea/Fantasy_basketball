import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

/* ---------- GET ---------- */

export const getPlayers = () =>
  api.get("/players");

export const getRankings = () =>
  api.get("/rankings");

export const getSchedule = () =>
  api.get("/schedule");

export const healthCheck = () =>
  api.get("/health");

/* ---------- POST ---------- */

export const getReplacements = (team: string[]) =>
  api.post("/replacements", { team });

export const getBoomBust = (team: string[]) =>
  api.post("/boombust", { team });

export const analyzeTrade = (trade: unknown) =>
  api.post("/trade", { trade });

export default api;
