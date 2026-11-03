import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

export function MarketingShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return <div className="min-h-screen bg-[#faf7ef] text-[#263b37]">
    <div className="border-b border-[#dce4d8] bg-[#edf4e9] px-5 py-2 text-center text-[11px] font-semibold uppercase tracking-[.12em] text-[#426655]">Private beta · Browser voice calls</div>
    <SiteHeader />
    {children}
    <SiteFooter />
  </div>;
}
