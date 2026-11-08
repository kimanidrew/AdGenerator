"use client";
import { FormEvent, useState } from "react";
type Props = { mode: "login" | "signup" };
export default function AuthForm({ mode }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      const endpoint = mode === "signup" ? "signup" : "login";
      const response = await fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/auth/" + endpoint, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify(mode === "signup" ? {email, password, allow_ai_training: consent} : {email, password}),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
      sessionStorage.setItem("kenyaads_access_token", data.access_token);
      window.location.href = "/";
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to connect to the API."); }
    finally { setBusy(false); }
  }
  return <form onSubmit={submit} className="w-full max-w-md rounded-3xl border border-white/10 bg-white/[.04] p-8">
    <h1 className="text-3xl font-black">{mode === "signup" ? "Create your account" : "Welcome back"}</h1>
    <p className="mt-2 text-sm text-slate-400">{mode === "signup" ? "Start building ads that speak Kenya." : "Log in to continue to KenyaAds AI."}</p>
    <label className="mt-7 block text-sm font-semibold">Email address<input required type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 outline-none focus:border-emerald-400"/></label>
    <label className="mt-5 block text-sm font-semibold">Password<input required minLength={10} type="password" autoComplete={mode === "signup" ? "new-password" : "current-password"} value={password} onChange={e => setPassword(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 outline-none focus:border-emerald-400"/><span className="mt-1 block text-xs text-slate-500">At least 10 characters.</span></label>
    {mode === "signup" && <label className="mt-5 flex gap-3 text-sm leading-6 text-slate-300"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} className="mt-1 h-4 w-4 accent-emerald-400"/><span>Allow my content to improve the AI. This is optional. You can use KenyaAds AI without agreeing. If accepted, your choice is timestamped.</span></label>}
    {error && <p role="alert" className="mt-4 rounded-xl bg-red-400/10 p-3 text-sm text-red-300">{error}</p>}
    <button disabled={busy} className="mt-7 w-full rounded-xl bg-emerald-400 px-4 py-3 font-bold text-slate-950 disabled:opacity-50">{busy ? "Please wait…" : mode === "signup" ? "Create account" : "Log in"}</button>
    <p className="mt-5 text-center text-sm text-slate-400">{mode === "signup" ? "Already registered?" : "New to KenyaAds AI?"} <a className="font-semibold text-emerald-300 underline" href={mode === "signup" ? "/login" : "/signup"}>{mode === "signup" ? "Log in" : "Create an account"}</a></p>
  </form>;
}
