import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Queue, api, clearToken, getToken } from "./api";

function money(n: number): string {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export default function QueuePage() {
  const navigate = useNavigate();
  const [queue, setQueue] = useState<Queue | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  async function load() {
    try {
      setQueue(await api.queue());
    } catch {
      clearToken();
      navigate("/login");
    }
  }

  useEffect(() => {
    if (!getToken()) {
      navigate("/login");
      return;
    }
    load().catch(() => undefined);
  }, [navigate]);

  async function ack(code: string) {
    setBusy(code);
    setError("");
    try {
      await api.ack(code);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ack failed");
    } finally {
      setBusy("");
    }
  }

  if (!queue) return <div className="layout">Loading…</div>;

  return (
    <div className="layout">
      <div className="top">
        <div>
          <h1>Week {queue.week} exceptions</h1>
          <p className="muted">
            {queue.n} open items · {money(queue.total_impact)} of recommended spend if ignored
          </p>
        </div>
        <button
          className="secondary"
          onClick={() => {
            clearToken();
            navigate("/login");
          }}
        >
          Sign out
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {queue.exceptions.map((row) => (
        <article key={row.code} className="card">
          <div className="row">
            <div>
              <div className="kind">{row.kind.replace(/_/g, " ")}</div>
              <h2 style={{ margin: "0.2rem 0 0.4rem", fontSize: "1.05rem" }}>{row.title}</h2>
              <p className="muted" style={{ margin: 0 }}>
                {row.recommendation}
              </p>
            </div>
            <div className="dollars">{money(row.dollar_impact)}</div>
          </div>
          <div className="row" style={{ marginTop: "0.75rem" }}>
            <span className="muted">{row.detail}</span>
            {row.acknowledged ? (
              <span className="acked">acknowledged</span>
            ) : (
              <button className="secondary" disabled={busy === row.code} onClick={() => ack(row.code)}>
                Take action
              </button>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
