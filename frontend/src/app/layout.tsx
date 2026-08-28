import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VANGUARD — AI Defense Lab | Mastercard Innovation Challenge 2026",
  description: "Adversarial Evolution & Generative Intelligence Shield — Red Team/Blue Team AI system for payment fraud defense",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-vanguard-bg text-vanguard-text antialiased">
        {children}
      </body>
    </html>
  );
}
