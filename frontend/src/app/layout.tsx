import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Protein Embedding Workbench",
  description: "Explore protein embeddings, cache status, and similarity search.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
