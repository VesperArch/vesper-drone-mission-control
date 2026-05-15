import client from "./client";

export const fetchMissions = () => client.get("/missions/").then((r) => r.data);
export const fetchMission  = (id) => client.get(`/missions/${id}/`).then((r) => r.data);
export const createMission = (data) => client.post("/missions/create/", data).then((r) => r.data);
export const fetchLogs     = () => client.get("/missions/logs/").then((r) => r.data);
