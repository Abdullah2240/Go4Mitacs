export const metadata = { title: "Mitacs Matcher", description: "Private project matching workspace" };
import "./globals.css";
import localFont from "next/font/local";

const geist = localFont({ src: [{ path: "./fonts/Inter-Regular.ttf", weight: "400" }, { path: "./fonts/Inter-Medium.ttf", weight: "500" }, { path: "./fonts/Inter-SemiBold.ttf", weight: "600" }, { path: "./fonts/Inter-Bold.ttf", weight: "700" }], variable: "--font-sans", display: "swap" });
const newsreader = localFont({ src: [{ path: "./fonts/Newsreader-Regular.ttf", weight: "400" }, { path: "./fonts/Newsreader-Medium.ttf", weight: "500" }, { path: "./fonts/Newsreader-SemiBold.ttf", weight: "600" }, { path: "./fonts/Newsreader-Bold.ttf", weight: "700" }], variable: "--font-display", display: "swap" });

const themeInitScript = `(function(){try{var t=localStorage.getItem("mitacs:theme");if(!t){t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}document.documentElement.setAttribute("data-theme",t);}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><head><script dangerouslySetInnerHTML={{ __html: themeInitScript }} /></head><body className={`${geist.variable} ${newsreader.variable}`}>{children}</body></html>;
}
