"use client";
import { useState } from "react";
export default function Page() {
  const [m, setM] = useState("");
  async function submit(e: any) {
    e.preventDefault();
    setM("Submitting...");
    const r = await fetch(
      process.env.NEXT_PUBLIC_INTAKE_API_URL ||
        "http://localhost:8000/v1/leads",
      { method: "POST", body: new FormData(e.currentTarget) },
    );
    setM(
      r.ok
        ? "Thank you. We received your application."
        : "Submission failed. Please try again.",
    );
    if (r.ok) e.currentTarget.reset();
  }
  return (
    <main>
      <h1>Apply with us</h1>
      <form onSubmit={submit}>
        <label>
          First name
          <input name="first_name" required />
        </label>
        <label>
          Last name
          <input name="last_name" required />
        </label>
        <label>
          Email
          <input name="email" type="email" required />
        </label>
        <label>
          Resume / CV
          <input name="resume" type="file" accept=".pdf,.doc,.docx" required />
        </label>
        <button>Submit application</button>
      </form>
      <p>{m}</p>
      <style jsx>{`
        label {
          display: block;
          margin: 14px 0;
        }
        input {
          display: block;
          width: 100%;
          padding: 8px;
          margin-top: 4px;
        }
        button {
          padding: 10px;
        }
      `}</style>
    </main>
  );
}
