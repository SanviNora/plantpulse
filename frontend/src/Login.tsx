import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "./api";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("planner@plantpulse.example.com");
  const [password, setPassword] = useState("planner-password");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.login(email, password);
      navigate("/");
    } catch {
      setError("login failed");
    }
  }

  return (
    <div className="layout">
      <h1>PlantPulse</h1>
      <p className="muted">S&OP exception desk for the Fort Worth / Singapore lens network.</p>
      <form className="card" onSubmit={onSubmit} style={{ maxWidth: 420 }}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="error">{error}</p>}
        <div style={{ marginTop: "1rem" }}>
          <button type="submit">Sign in</button>
        </div>
      </form>
    </div>
  );
}
