import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import CreateMission from "./pages/CreateMission";
import ActiveMissions from "./pages/ActiveMissions";
import MissionLogs from "./pages/MissionLogs";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"       element={<Dashboard />} />
        <Route path="create-mission"  element={<CreateMission />} />
        <Route path="missions"        element={<ActiveMissions />} />
        <Route path="logs"            element={<MissionLogs />} />
      </Route>
    </Routes>
  );
}
