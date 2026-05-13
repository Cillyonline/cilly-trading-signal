import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cilly Trading Signal",
  description: "Trading cockpit fuer Long-only Swingtrading.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
