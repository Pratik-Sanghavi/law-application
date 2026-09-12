"use client";
import { useState } from "react";
export default function Page() {
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  async function submit(e: any) {
    e.preventDefault();
    setSending(true);
    setError("");
    const r = await fetch(
      process.env.NEXT_PUBLIC_INTAKE_API_URL ||
        "http://localhost:8000/v1/leads",
      { method: "POST", body: new FormData(e.currentTarget) },
    );
    setSending(false);
    if (r.ok) {
      setDone(true);
      e.currentTarget.reset();
    } else
      setError(
        "We could not submit your application. Please try again in a moment.",
      );
  }
  if (done)
    return (
      <div className="shell">
        <div className="success card">
          <div className="success-icon">âœ“</div>
          <div className="eyebrow">Application received</div>
          <h1>Thank you for reaching out.</h1>
          <p className="muted">
            Your details and resume are safely with our team. We will be in
            touch if there is a good fit.
          </p>
          <button className="button secondary" onClick={() => setDone(false)}>
            Submit another inquiry
          </button>
        </div>
      </div>
    );
  return (
    <div className="shell">
      <header className="topbar">
        <span className="brand">Almanac</span>
        <span className="muted">Careers</span>
      </header>
      <section className="hero">
        <div className="eyebrow">Immigration guidance</div>
        <h1>Navigate immigration with Almanac.</h1>
        <p>
          Tell us a little about yourself and upload your resume. It takes less
          than two minutes.
        </p>
      </section>
      <form className="card form-card" onSubmit={submit}>
        <label className="field">
          First name
          <input className="input" name="first_name" required />
        </label>
        <label className="field">
          Last name
          <input className="input" name="last_name" required />
        </label>
        <label className="field">
          Email address
          <input className="input" name="email" type="email" required />
        </label>
        <label className="field">
          Resume or CV
          <input
            className="input"
            name="resume"
            type="file"
            accept=".pdf,.doc,.docx"
            required
          />
        </label>
        <p className="muted" style={{ fontSize: 13 }}>
          PDF, DOC, or DOCX. Maximum file size: 10 MB.
        </p>
        <button className="button" disabled={sending}>
          {sending ? "Submittingâ€¦" : "Submit application"}
        </button>
        {error && <p className="notice">{error}</p>}
      </form>
    </div>
  );
}
