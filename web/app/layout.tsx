import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "KenyaAds AI", description: "Create short-form adverts with a Kenyan voice and feel." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
