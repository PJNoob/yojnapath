"use client";

import { useState } from "react";
import { Mic, MicOff, Phone, PhoneOff } from "lucide-react";
import { useWebCall } from "./use-web-call";

function timeLabel(seconds: number) {
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}

export function CallScreen() {
  const call = useWebCall();
  const [accessCode, setAccessCode] = useState("");
  const active = call.state === "active";
  const scale = 1 + call.audioLevel * 0.13;

  return (
    <main className="relative flex min-h-[100svh] flex-col overflow-hidden bg-[#fbf7ef] px-5 pb-8 pt-6 text-center text-[#263b37] sm:px-8">
      <div className="pointer-events-none absolute -left-24 top-1/3 size-72 rounded-full bg-[#e5eee5] blur-3xl" />
      <div className="pointer-events-none absolute -right-28 bottom-0 size-80 rounded-full bg-[#f6e5d7] blur-3xl" />
      <header className="relative mx-auto flex w-full max-w-lg items-center justify-between border-b border-[#d9dfd5] pb-5 text-left">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#668179]">YojnaPath voice</p>
          <p className="mt-1 text-sm font-medium text-[#526a63]">Government-scheme questions, by voice</p>
        </div>
        <span className="rounded-full border border-[#d9dfd5] bg-white/75 px-3 py-1.5 text-xs font-semibold tabular-nums text-[#526a63]">
          {active ? timeLabel(call.seconds) : "Web call beta"}
        </span>
      </header>

      <section className="relative mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center py-12" aria-live="polite">
        <>
            <div className="relative grid h-56 w-56 place-items-center">
              <span className="absolute h-52 w-52 rounded-full border border-[#c9d9c9] bg-white/35 transition-transform duration-150" style={{ transform: `scale(${scale * 1.13})` }} />
              <span className="absolute h-40 w-40 rounded-full border border-[#e7d0bb] bg-[#f5e5d7]/65 transition-transform duration-150" style={{ transform: `scale(${scale})` }} />
              <div className="relative grid h-28 w-28 place-items-center rounded-full bg-[#3f695c] text-5xl font-medium text-white shadow-[0_18px_45px_rgba(57,98,82,.25)]">S</div>
            </div>
            <p className="mt-8 text-[11px] font-bold uppercase tracking-[0.2em] text-[#8b8f75]">Your scheme guide</p>
            <h1 className="mt-2 font-serif text-4xl font-semibold">YojnaPath Sahayak</h1>
            <p className="mt-3 max-w-xs leading-7 text-[#65756e]">{active ? "Ask your question in Hindi or Hinglish." : call.message}</p>
            {active && <p className="mt-5 inline-flex items-center gap-2 rounded-full bg-[#e8f1e8] px-4 py-2 text-xs font-semibold text-[#426655]"><span className="size-2 rounded-full bg-[#5b9d68]" />Call in progress</p>}
        </>
      </section>

      <div className="relative mx-auto w-full max-w-lg">
        {(call.state === "ready" || call.state === "ended" || call.state === "error") && <form onSubmit={(event) => { event.preventDefault(); void call.startCall(accessCode); }} className="space-y-3">
          <label htmlFor="web-call-code" className="block text-left text-sm font-semibold text-[#426655]">Private beta access code</label>
          <input id="web-call-code" type="password" autoComplete="off" value={accessCode} onChange={(event) => setAccessCode(event.target.value)} placeholder="Enter access code" required className="w-full rounded-2xl border border-[#cbd9cb] bg-white px-5 py-4 text-[#263b37] outline-none focus:border-[#3f695c] focus:ring-2 focus:ring-[#3f695c]/20" />
          <button type="submit" className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-[#3f695c] px-8 py-4 font-semibold text-white shadow-[0_12px_30px_rgba(57,98,82,.2)] transition hover:bg-[#31584d]"><Phone size={18} />{call.state === "ready" ? "Start web call" : "Call again"}</button>
        </form>}
        {(call.state === "connecting" || active) && <nav className="flex justify-center gap-5 rounded-[2rem] border border-[#d9dfd5] bg-white/80 px-8 py-5 shadow-[0_12px_35px_rgba(68,75,56,.07)]" aria-label="Call controls">
          <button type="button" onClick={() => void call.toggleMute()} disabled={!active} className="grid h-14 w-14 place-items-center rounded-full bg-[#e8f0e8] text-[#31584d] disabled:opacity-40" aria-label={call.muted ? "Unmute" : "Mute"}>{call.muted ? <MicOff size={23} /> : <Mic size={23} />}</button>
          <button type="button" onClick={() => void call.endCall()} className="grid h-14 w-14 place-items-center rounded-full bg-[#b7524d] text-white" aria-label="End call"><PhoneOff size={23} /></button>
        </nav>}
        {call.state === "error" && <p role="alert" className="mt-3 rounded-2xl border border-[#e8d9c9] bg-white/80 px-5 py-4 text-sm text-[#9b4540]">{call.message}</p>}
        <p className="mt-4 text-xs leading-5 text-[#65756e]">Your browser will ask for microphone access when you start the call.</p>
        <p className="mt-5 text-xs leading-5 text-[#8a958c]">General guidance only. Verify current scheme details with official government sources. Never share Aadhaar, bank details, passwords, or OTPs.</p>
      </div>
    </main>
  );
}
