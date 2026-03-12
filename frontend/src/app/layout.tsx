import type { Metadata, Viewport } from "next";
import "./globals.css";
import { BottomNav } from "@/components/BottomNav";

export const metadata: Metadata = {
  title: "Дневник тренировок",
  description: "Персональный дневник тренировок с аналитикой",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#6366f1",
};

import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="pb-20 bg-white dark:bg-gray-900 text-black dark:text-white">
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <main className="max-w-lg mx-auto px-4 pt-4">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
