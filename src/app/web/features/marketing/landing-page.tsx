import Link from "next/link";
import { ArrowRight, AudioLines, Check, MessageCircle, Phone, ShieldCheck } from "lucide-react";

const steps = [
  { number: "01", title: "Ask naturally", copy: "Start with a specific scheme question or tell the guide what kind of support you are looking for." },
  { number: "02", title: "Explore together", copy: "The guide listens, asks one question at a time, and helps you understand possible next steps." },
  { number: "03", title: "Check the source", copy: "Confirm eligibility, documents, dates, and application steps on an official government portal." },
];

export function LandingPage() {
  return <main>
    <section className="relative overflow-hidden bg-[#faf7ef] px-5 py-20 lg:px-8 lg:py-28">
      <div className="pointer-events-none absolute -right-20 top-0 size-96 rounded-full bg-[#f1dcc8]/60 blur-3xl" />
      <div className="pointer-events-none absolute -left-28 bottom-0 size-80 rounded-full bg-[#dfeadf]/70 blur-3xl" />
      <div className="relative mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[1.05fr_.95fr]">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-[#d5e3d4] bg-[#eff4ec] px-4 py-2 text-xs font-bold uppercase tracking-[.12em] text-[#426655]"><AudioLines size={15} /> Government-scheme guidance by voice</span>
          <h1 className="mt-7 font-serif text-5xl font-semibold leading-[1.04] tracking-tight text-[#263b37] sm:text-6xl lg:text-7xl">A simpler way to ask about <span className="text-[#3f695c]">sarkari yojanas.</span></h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[#65756e]">Speak in Hindi or Hinglish. YojnaPath helps you frame your question, understand general steps, and find what to verify next.</p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link href="/call" className="inline-flex min-h-13 items-center justify-center gap-2 rounded-full bg-[#3f695c] px-7 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(57,98,82,.2)] hover:bg-[#31584d]"><Phone size={17} /> Start a web call <ArrowRight size={17} /></Link>
            <Link href="#how-it-works" className="inline-flex min-h-13 items-center justify-center rounded-full border border-[#cbd9cb] bg-white px-7 text-sm font-semibold text-[#31584d] hover:border-[#3f695c]">How it works</Link>
          </div>
          <p className="mt-6 text-sm text-[#74837a]">Private beta access code required · No telephone number needed</p>
        </div>
        <div className="relative mx-auto w-full max-w-md rounded-[2rem] border border-[#dce5d8] bg-white/85 p-7 shadow-[0_30px_70px_rgba(59,88,68,.11)] sm:p-9">
          <div className="flex items-center justify-between"><span className="text-xs font-bold uppercase tracking-[.15em] text-[#8a958c]">A conversation with</span><span className="rounded-full bg-[#e8f1e8] px-3 py-1 text-xs font-semibold text-[#426655]">Voice beta</span></div>
          <div className="mt-10 flex items-center gap-5"><span className="grid size-20 shrink-0 place-items-center rounded-full bg-[#3f695c] text-white"><AudioLines size={33} /></span><div><p className="font-serif text-3xl font-semibold">YojnaPath</p><p className="mt-1 text-sm text-[#65756e]">Your patient scheme guide</p></div></div>
          <div className="mt-10 space-y-4"><div className="max-w-[85%] rounded-[1.3rem_1.3rem_1.3rem_.3rem] bg-[#f1f5ee] p-4 text-sm leading-6 text-[#31584d]">Namaste! Kisi khaas yojana ke baare mein sawaal hai?</div><div className="ml-auto max-w-[82%] rounded-[1.3rem_1.3rem_.3rem_1.3rem] bg-[#e9dacb] p-4 text-sm leading-6 text-[#604b3b]">Mujhe housing support ke baare mein samajhna hai.</div></div>
          <div className="mt-8 flex items-center justify-between border-t border-[#e4e8df] pt-5 text-xs font-semibold text-[#74837a]"><span>One question at a time</span><AudioLines size={24} className="text-[#3f695c]" /></div>
        </div>
      </div>
    </section>

    <section id="how-it-works" className="border-y border-[#e7e2d7] bg-[#f2f4ec] px-5 py-20 lg:px-8">
      <div className="mx-auto max-w-7xl"><p className="text-xs font-bold uppercase tracking-[.15em] text-[#426655]">How a call flows</p><h2 className="mt-4 max-w-2xl font-serif text-4xl font-semibold leading-tight sm:text-5xl">A familiar conversation, at your pace.</h2><div className="mt-12 grid gap-5 md:grid-cols-3">{steps.map((step) => <article key={step.number} className="rounded-[1.5rem] border border-[#e0e5da] bg-white p-7"><span className="text-xs font-bold tracking-[.15em] text-[#ad7a5f]">{step.number}</span><h3 className="mt-8 font-serif text-2xl font-semibold">{step.title}</h3><p className="mt-3 text-sm leading-7 text-[#65756e]">{step.copy}</p></article>)}</div></div>
    </section>

    <section id="about" className="px-5 py-20 lg:px-8"><div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-2"><div><p className="text-xs font-bold uppercase tracking-[.15em] text-[#426655]">Built for clarity</p><h2 className="mt-4 font-serif text-4xl font-semibold leading-tight sm:text-5xl">Ask without a form or a long search.</h2><p className="mt-5 text-base leading-8 text-[#65756e]">The browser call uses your microphone and a live AI voice agent. It can help you organise a question and understand broad categories. You can end the call at any time.</p></div><div className="rounded-[1.75rem] border border-[#dce5d8] bg-[#e8f0e7] p-8"><ShieldCheck size={28} className="text-[#3f695c]" /><h3 className="mt-5 font-serif text-2xl font-semibold">Important before you apply</h3><p className="mt-4 text-sm leading-7 text-[#526a63]">YojnaPath does not have a live, verified scheme database yet. It cannot confirm current eligibility, benefits, deadlines, or application status. Check those details with the relevant official government source.</p><div className="mt-6 flex flex-wrap gap-3 text-xs font-semibold text-[#426655]"><span className="inline-flex items-center gap-1"><Check size={14} /> No Aadhaar or OTP needed</span><span className="inline-flex items-center gap-1"><MessageCircle size={14} /> Hindi and Hinglish</span></div></div></div></section>
  </main>;
}
