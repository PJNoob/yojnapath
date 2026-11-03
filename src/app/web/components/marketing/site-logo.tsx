import Link from "next/link";
import { AudioLines } from "lucide-react";

export function SiteLogo() {
  return <Link href="/" className="inline-flex items-center gap-2.5 font-semibold text-[#263b37]" aria-label="YojnaPath home">
    <span className="grid size-9 place-items-center rounded-xl bg-[#3f695c] text-white"><AudioLines size={20} /></span>
    <span className="font-serif text-xl tracking-tight">YojnaPath</span>
  </Link>;
}
