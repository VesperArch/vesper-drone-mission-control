import client from "./client";

export const fetchStatus   = () => client.get("/system/status/").then((r) => r.data);
export const fetchMetadata = () => client.get("/system/metadata/").then((r) => r.data);
