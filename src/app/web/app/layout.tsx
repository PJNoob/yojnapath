import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: "YojnaPath", template: "%s | YojnaPath" },
  description: "A voice-first guide to government-scheme questions in Hindi and Hinglish.",
  openGraph: {
    type: "website",
    siteName: "YojnaPath",
    title: "YojnaPath",
    description: "Ask about government schemes in a natural voice conversation.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
