import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {routing} from '@/i18n/routing';
import {notFound} from 'next/navigation';
import { Providers } from '@/components/shared/providers';
import { MainLayout } from '@/components/shared/main-layout';
import { Inter, Lexend } from "next/font/google";
import { Metadata } from "next";
import '../globals.css';

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const lexend = Lexend({
  variable: "--font-lexend",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "EduPath AI Navigator",
  description: "Your AI-powered personalized learning journey",
};

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const { locale } = await params;
  
  if (!routing.locales.includes(locale as "en" | "ru")) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale} className={`${inter.variable} ${lexend.variable} h-full antialiased`} suppressHydrationWarning>
      <body className="h-full bg-background font-lexend text-foreground">
        <Providers>
          <NextIntlClientProvider messages={messages}>
            <MainLayout>
              {children}
            </MainLayout>
          </NextIntlClientProvider>
        </Providers>
      </body>
    </html>
  );
}
