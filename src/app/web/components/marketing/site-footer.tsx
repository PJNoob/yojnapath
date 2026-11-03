import Link from "next/link";
import { SiteLogo } from "./site-logo";

export function SiteFooter() {
  return <footer className="border-t border-[#e7e2d7] bg-[#f1f3eb] px-5 py-10 lg:px-8">
    <div className="mx-auto flex max-w-7xl flex-col justify-between gap-6 sm:flex-row sm:items-end">
      <div><SiteLogo /><p className="mt-3 max-w-md text-sm leading-6 text-[#65756e]">A private beta voice guide for government-scheme questions. Verify current details with official sources before applying.</p></div>
      <div className="flex gap-5 text-sm font-medium text-[#426655]"><Link href="/#how-it-works">How it works</Link><Link href="/call">Web call</Link></div>
    </div>
  </footer>;
}
