"use client";

import { FormEvent, useState } from "react";

export default function Page() {
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setSending(true);
    setError("");

    try {
      const response = await fetch(
        process.env.NEXT_PUBLIC_INTAKE_API_URL ||
          "http://localhost:8000/v1/leads",
        { method: "POST", body: new FormData(form) },
      );

      if (!response.ok) {
        throw new Error("Submission failed");
      }

      form.reset();
      setDone(true);
    } catch {
      setError(
        "We could not submit your application. Please try again in a moment.",
      );
    } finally {
      setSending(false);
    }
  }

  if (done) {
    return (
      <main className="shell">
        <section className="success card" aria-live="polite">
          <div className="success-icon" aria-hidden="true">
            &#10003;
          </div>
          <h1>Your submission has been recorded.</h1>
          <p className="muted">
            One of our attorneys will get in touch with you soon.
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="topbar">
        <span className="brand">Almanac</span>
      </header>
      <section className="hero">
        <div className="eyebrow">Immigration guidance</div>
        <h1>Navigate immigration with Almanac.</h1>
        <p>
          Share your details and resume so our immigration team can understand
          how to help.
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
          {sending ? "Submitting..." : "Submit application"}
        </button>
        {error && <p className="notice">{error}</p>}
      </form>
    </main>
  );
}
