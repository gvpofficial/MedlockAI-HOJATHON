import './globals.css';
import NavigationHeader from '@/components/dashboard/NavigationHeader';
import { ShieldCheck, AlertCircle } from 'lucide-react';

export const metadata = {
  title: 'MEDLOCK AI — Agentic Cross-Pharmacy Prescription Integrity System',
  description: 'A secure multi-agent digital prescription and medicine-dispensing system preventing cross-pharmacy over-dispensing.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased">
        <NavigationHeader />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer className="border-t border-slate-200 bg-white py-8 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-xs">
                M
              </div>
              <span className="font-semibold text-slate-700">MEDLOCK AI</span>
              <span>— Agentic Cross-Pharmacy Prescription Integrity System</span>
            </div>

            <div className="flex items-center gap-2 bg-amber-50 text-amber-800 px-3 py-1.5 rounded-xl border border-amber-200/80">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span>
                Hackathon Prototype & Demo System. High-risk actions require authorized human pharmacist review.
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
