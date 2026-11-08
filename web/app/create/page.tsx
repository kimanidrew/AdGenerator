"use client";

import { FormEvent, useEffect, useState } from "react";

type Scene = {
  scene_number: number;
  duration_seconds: number;
  visual_direction: string;
  voiceover: string;
  on_screen_text: string;
  transition: string;
};
type StoryboardImage = { scene_number: number; image_url: string; prompt: string };
type Script = {
  title: string;
  product_name: string;
  language: string;
  duration_seconds: number;
  platform: string;
  tone: string;
  target_audience: string;
  scenes: Scene[];
  caption: string;
  hashtags: string[];
  call_to_action: string;
};
const inputClass = "mt-2 w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400";
const labelClass = "block text-sm font-semibold text-slate-300";

type ApiResponse = { detail?: string; [key: string]: unknown };

async function readApiResponse(response: Response): Promise<ApiResponse> {
  const body = await response.text();
  if (!body) return {};
  try {
    return JSON.parse(body) as ApiResponse;
  } catch {
    return {
      detail: body.trim() || `Server returned HTTP ${response.status}.`,
    };
  }
}

export default function CreatePage() {
  const [brief, setBrief] = useState("");
  const [productName, setProductName] = useState("");
  const [industry, setIndustry] = useState("Food & beverages");
  const [audience, setAudience] = useState("Everyday Kenyan consumers");
  const [language, setLanguage] = useState("Sheng");
  const [duration, setDuration] = useState("15");
  const [platform, setPlatform] = useState("TikTok");
  const [tone, setTone] = useState("Energetic");
  const [script, setScript] = useState<Script | null>(null);
  const [mode, setMode] = useState("");
  const [storyboard, setStoryboard] = useState<StoryboardImage[]>([]);
  const [storyboardBusy, setStoryboardBusy] = useState(false);
  const [storyboardStatus, setStoryboardStatus] = useState("");
  const [storyboardError, setStoryboardError] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    if (!sessionStorage.getItem("kenyaads_access_token")) {
      window.location.replace("/login");
      return;
    }
    setCheckingSession(false);
  }, []);

  async function generate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setScript(null);
    setStoryboard([]);
    setStoryboardError("");
    try {
      const token = sessionStorage.getItem("kenyaads_access_token");
      const apiBase = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const response = await fetch(`${apiBase}/api/scripts/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          brief, product_name: productName || "Your product", industry, audience,
          language, duration_seconds: Number(duration), platform, tone,
        }),
      });
      const data = await readApiResponse(response);
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Could not generate your script.");
      setScript(data.script);
      setMode(data.generation_mode);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reach KenyaAds AI. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  async function generateStoryboard() {
    if (!script) return;
    setStoryboardBusy(true);
    setStoryboardError("");
    setStoryboardStatus("Submitting storyboard job…");
    setStoryboard([]);
    try {
      const token = sessionStorage.getItem("kenyaads_access_token");
      const apiBase = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const headers = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };
      const response = await fetch(`${apiBase}/api/storyboards/generate`, {
        method: "POST", headers, body: JSON.stringify({ script }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Could not start storyboard generation.");
      const jobId = data.job_id as string;
      for (let attempt = 0; attempt < 180; attempt += 1) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const statusResponse = await fetch(`${apiBase}/api/storyboards/jobs/${jobId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const statusData = await readApiResponse(statusResponse);
        if (!statusResponse.ok) throw new Error(typeof statusData.detail === "string" ? statusData.detail : "Could not check storyboard progress.");
        if (statusData.status === "completed") {
          setStoryboard(statusData.images || []);
          setStoryboardStatus("");
          return;
        }
        setStoryboardStatus(statusData.status === "processing"
          ? `Generating scene images… ${statusData.completed_scenes || 0}/${statusData.total_scenes || script.scenes.length}`
          : "Waiting for the image worker…");
      }
      throw new Error("Storyboard generation is taking longer than expected. Your job may still be running; please try again shortly.");
    } catch (err) {
      setStoryboardError(err instanceof Error ? err.message : "Unable to generate storyboard. Please try again.");
      setStoryboardStatus("");
    } finally {
      setStoryboardBusy(false);
    }
  }

  function updateScene(index: number, field: keyof Scene, value: string) {
    setScript(current => current ? {
      ...current,
      scenes: current.scenes.map((scene, i) => i === index
        ? { ...scene, [field]: field === "duration_seconds" ? Number(value) : value }
        : scene),
    } : current);
  }

  if (checkingSession) return <main className="flex min-h-screen items-center justify-center text-sm text-slate-400">Checking your session…</main>;

  return (
    <main className="min-h-screen bg-[#080b12] px-5 py-8 text-white md:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-10 flex items-center justify-between">
          <a href="/" className="text-lg font-black tracking-tight">KENYA<span className="text-emerald-400">ADS</span> AI</a>
          <a href="/" className="text-sm text-slate-400 transition hover:text-white">Back to home</a>
        </header>
        <div className="mb-8 max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[.22em] text-emerald-300">Script + storyboard studio</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight md:text-5xl">Turn your idea into a script.</h1>
          <p className="mt-4 leading-7 text-slate-400">Describe what you are advertising. KenyaAds AI will organise it into scenes with visuals, voiceover and on-screen text you can edit.</p>
        </div>

        <div className="grid items-start gap-7 lg:grid-cols-[.85fr_1.15fr]">
          <form onSubmit={generate} className="rounded-3xl border border-white/10 bg-white/[.035] p-6 md:p-7">
            <h2 className="text-xl font-bold">Your advert brief</h2>
            <label className={`${labelClass} mt-6`}>What are you advertising?
              <textarea required minLength={10} maxLength={1200} rows={5} value={brief} onChange={e => setBrief(e.target.value)} placeholder="Example: A refreshing soda for young people in Nairobi. Show friends enjoying it after a football match in a lively estate." className={`${inputClass} resize-y`} />
            </label>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className={labelClass}>Product / business name<input value={productName} onChange={e => setProductName(e.target.value)} placeholder="e.g. Maji Fresh" className={inputClass}/></label>
              <label className={labelClass}>Industry<select value={industry} onChange={e => setIndustry(e.target.value)} className={inputClass}>{["Food & beverages","Fashion","Beauty","Technology","Mobile money","Transport","Education","Real estate","Hospitality","General"].map(x => <option key={x}>{x}</option>)}</select></label>
              <label className={labelClass}>Language<select value={language} onChange={e => setLanguage(e.target.value)} className={inputClass}>{["Sheng","Kiswahili","English"].map(x => <option key={x}>{x}</option>)}</select></label>
              <label className={labelClass}>Duration<select value={duration} onChange={e => setDuration(e.target.value)} className={inputClass}>{["10","15","20","30","45","60"].map(x => <option key={x} value={x}>{x} seconds</option>)}</select></label>
              <label className={labelClass}>Platform<select value={platform} onChange={e => setPlatform(e.target.value)} className={inputClass}>{["TikTok","Instagram Reels","YouTube Shorts","Facebook"].map(x => <option key={x}>{x}</option>)}</select></label>
              <label className={labelClass}>Tone<select value={tone} onChange={e => setTone(e.target.value)} className={inputClass}>{["Energetic","Funny","Premium","Friendly","Inspirational","Trustworthy"].map(x => <option key={x}>{x}</option>)}</select></label>
            </div>
            <label className={`${labelClass} mt-5`}>Target audience<input value={audience} onChange={e => setAudience(e.target.value)} maxLength={160} className={inputClass}/></label>
            {error && <p role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/10 p-3 text-sm text-red-300">{error}</p>}
            <button disabled={busy} className="mt-7 w-full rounded-xl bg-emerald-400 px-5 py-4 font-bold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-wait disabled:opacity-60">{busy ? "Writing your script…" : "Generate script →"}</button>
            <p className="mt-3 text-center text-xs leading-5 text-slate-500">Edit your scenes, then generate a visual storyboard for each scene.</p>
          </form>

          <section className="min-w-0 rounded-3xl border border-white/10 bg-white/[.025] p-6 md:p-7">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div><p className="text-xs font-bold uppercase tracking-[.2em] text-slate-500">Your script</p><h2 className="mt-2 text-xl font-bold">Scene-by-scene draft</h2></div>
              {script && <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1.5 text-xs font-semibold text-emerald-200">{mode === "self_hosted_llm" ? "AI model draft" : "Starter draft"}</span>}
            </div>
            {!script ? (
              <div className="mt-6 flex min-h-[420px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 px-8 text-center">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-400/10 text-2xl text-emerald-300">✦</div>
                <h3 className="font-semibold">Your script will appear here</h3>
                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">Fill in your advert brief and generate a draft. You will be able to edit the visuals, voiceover and text for every scene.</p>
              </div>
            ) : (
              <div className="mt-6 space-y-5">
                <div className="rounded-2xl bg-emerald-400/[.07] p-4">
                  <input aria-label="Script title" value={script.title} onChange={e => setScript({...script,title:e.target.value})} className="w-full bg-transparent text-lg font-bold outline-none"/>
                  <p className="mt-2 text-xs text-slate-400">{script.duration_seconds}s · {script.language} · {script.platform} · {script.tone}</p>
                </div>
                {script.scenes.map((scene,index) => (
                  <article key={scene.scene_number} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                    <div className="mb-4 flex items-center justify-between"><h3 className="font-bold">Scene {scene.scene_number}</h3><label className="text-xs text-slate-400">Seconds <input type="number" min="1" max="20" value={scene.duration_seconds} onChange={e=>updateScene(index,"duration_seconds",e.target.value)} className="ml-2 w-14 rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-center text-white"/></label></div>
                    <label className={labelClass}>Visual direction<textarea rows={2} value={scene.visual_direction} onChange={e=>updateScene(index,"visual_direction",e.target.value)} className={`${inputClass} resize-y`}/></label>
                    <label className={`${labelClass} mt-4`}>Voiceover<textarea rows={2} value={scene.voiceover} onChange={e=>updateScene(index,"voiceover",e.target.value)} className={`${inputClass} resize-y`}/></label>
                    <label className={`${labelClass} mt-4`}>On-screen text<input value={scene.on_screen_text} onChange={e=>updateScene(index,"on_screen_text",e.target.value)} className={inputClass}/></label>
                  </article>
                ))}
                <label className={labelClass}>Social caption<textarea rows={3} value={script.caption} onChange={e=>setScript({...script,caption:e.target.value})} className={`${inputClass} resize-y`}/></label>
                <label className={`${labelClass} mt-4`}>Call to action<input value={script.call_to_action} onChange={e=>setScript({...script,call_to_action:e.target.value})} className={inputClass}/></label>
                <label className={`${labelClass} mt-4`}>Hashtags<input value={script.hashtags.join(" ")} onChange={e=>setScript({...script,hashtags:e.target.value.split(/\s+/).filter(Boolean)})} className={inputClass}/></label>
                <div className="flex flex-wrap gap-3 pt-2">
                  <button type="button" disabled={storyboardBusy} onClick={generateStoryboard} className="rounded-xl bg-emerald-400 px-4 py-3 text-sm font-bold text-slate-950 hover:bg-emerald-300 disabled:opacity-60">{storyboardBusy ? "Generating scene images…" : "Generate storyboard images →"}</button>
                  <button type="button" onClick={()=>navigator.clipboard.writeText(JSON.stringify(script,null,2))} className="rounded-xl border border-white/15 px-4 py-3 text-sm font-semibold hover:bg-white/5">Copy script JSON</button>
                  <button type="button" onClick={()=>navigator.clipboard.writeText(script.scenes.map(s=>s.voiceover).join("\n\n"))} className="rounded-xl border border-white/15 px-4 py-3 text-sm font-semibold hover:bg-white/5">Copy voiceover</button>
                </div>
                {storyboardStatus && <p className="rounded-xl border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm text-emerald-200">{storyboardStatus}</p>}
                {storyboardError && <p role="alert" className="rounded-xl border border-red-400/20 bg-red-400/10 p-3 text-sm text-red-300">{storyboardError}</p>}
                {storyboard.length > 0 && <section className="space-y-4 pt-4"><div><p className="text-xs font-bold uppercase tracking-[.2em] text-emerald-300">Phase 3 · Storyboard</p><h3 className="mt-2 text-xl font-bold">Your scene visuals</h3><p className="mt-1 text-sm text-slate-400">Images are stored privately. Preview links expire after 15 minutes.</p></div><div className="grid gap-4 sm:grid-cols-2">{storyboard.map(item => <article key={item.scene_number} className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60"><img src={item.image_url} alt={`Storyboard scene ${item.scene_number}`} className="aspect-[9/16] w-full object-cover" /><div className="p-3"><p className="font-semibold">Scene {item.scene_number}</p><p className="mt-1 text-xs leading-5 text-slate-400">{item.prompt}</p></div></article>)}</div></section>}
                <p className="text-xs leading-5 text-slate-500">This editable draft is held in this browser session. Saving to your account and generation history will be added in Phase 5.</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
