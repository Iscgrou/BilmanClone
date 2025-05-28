import "./globals.css";
import Sidebar from "../components/ui/sidebar";
import { I18nProvider } from "../components/i18n-provider";
import { AuthProvider } from "../contexts/AuthContext";

export const metadata = {
  title: "VPN Reseller Billing & Management Suite",
  description: "سامانه مدیریت فروش VPN",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl">
      <head />
      <body className="flex">
        <AuthProvider>
          <I18nProvider>
            <Sidebar />
            <main className="flex-1 min-h-screen p-6 bg-gray-50">
              {children}
            </main>
          </I18nProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
