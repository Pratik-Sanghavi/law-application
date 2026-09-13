"use client";
import { useEffect, useState } from "react";
type Lead = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  resume_filename: string;
  state: string;
  created_at: string;
};
export default function Page() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState("");
  async function load() {
    const r = await fetch("/api/leads", { cache: "no-store" });
    if (r.status === 401) {
      location.href = "/api/auth/login";
      return;
    }
    if (!r.ok) {
      setError("Could not load leads.");
      return;
    }
    setLeads((await r.json()).items);
  }
  useEffect(() => {
    load();
  }, []);
  async function mark(id: string) {
    const r = await fetch(`/api/leads/${id}/state`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: '{"state":"REACHED_OUT"}',
    });
    if (!r.ok) setError("Could not update this lead.");
    else load();
  }
  return (
    <div className="shell">
      <header className="topbar">
        <span className="brand">Almanac</span>
        <form action="/api/auth/logout" method="post">
          <button className="button secondary">Log out</button>
        </form>
      </header>
      <div className="toolbar">
        <div>
          <div className="eyebrow">Attorney workspace</div>
          <h1>Immigration leads</h1>
          <p className="muted">
            Review prospective-client inquiries and keep outreach status
            current.
          </p>
        </div>
        <button className="button secondary" onClick={load}>
          Refresh
        </button>
      </div>
      {error && <p className="notice">{error}</p>}
      <section className="card table-wrap">
        {leads.length === 0 ? (
          <div className="empty">
            No leads yet. New immigration inquiries will appear here.
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Resume</th>
                <th>Submitted</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {leads.map((x) => (
                <tr key={x.id}>
                  <td>
                    <strong>
                      {x.first_name} {x.last_name}
                    </strong>
                    <br />
                    <span className="muted">{x.email}</span>
                  </td>
                  <td>
                    <a className="link" href={`/api/leads/${x.id}/resume`}>
                      {x.resume_filename}
                    </a>
                  </td>
                  <td>{new Date(x.created_at).toLocaleDateString()}</td>
                  <td>
                    <span
                      className={`badge ${x.state === "REACHED_OUT" ? "done" : ""}`}
                    >
                      {x.state === "REACHED_OUT" ? "Reached out" : "Pending"}
                    </span>
                  </td>
                  <td>
                    {x.state === "PENDING" && (
                      <button className="button" onClick={() => mark(x.id)}>
                        Mark reached out
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
