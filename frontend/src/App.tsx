import { Navigate, Route, Routes } from "react-router-dom";
import { getToken } from "./api";
import Login from "./Login";
import QueuePage from "./Queue";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={getToken() ? <QueuePage /> : <Navigate to="/login" replace />} />
    </Routes>
  );
}
