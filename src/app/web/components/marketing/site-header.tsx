import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { navigation } from "@/content/site";
import { SiteLogo } from "./site-logo";

export function SiteHeader() {
  return <header className="sticky top-0 z-30 border-b border-[#e7e2d7] bg-[#faf7ef]/95 backdrop-blur-lg">
    <div className="mx-auto flex h-17 max-w-7xl items-center justify-between gap-5 px-5 lg:px-8">
      <SiteLogo />
      <nav className="hidden items-center gap-7 text-sm font-medium text-[#526a63] md:flex" aria-label="Primary navigation">
        {navigation.map((item) => <Link key={item.href} href={item.href} className="hover:text-[#3f695c]">{item.label}</Link>)}
      </nav>
      <Link href="/call" className="inline-flex min-h-10 items-center gap-1.5 rounded-full bg-[#3f695c] px-4 text-xs font-semibold text-white hover:bg-[#31584d] sm:px-5 sm:text-sm">Start web call <ArrowUpRight size={15} /></Link>
    </div>
  </header>;
}
