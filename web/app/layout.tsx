export const metadata = { title: "Mitacs Matcher", description: "Private project matching workspace" };
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
