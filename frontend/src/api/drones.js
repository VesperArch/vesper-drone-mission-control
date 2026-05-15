import client from "./client";

export const fetchDrones = () => client.get("/drones/").then((r) => r.data);
export const fetchDrone  = (id) => client.get(`/drones/${id}/`).then((r) => r.data);
