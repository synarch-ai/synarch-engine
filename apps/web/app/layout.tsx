import './globals.css'
import type { Metadata } from 'next'
import { Outfit, JetBrains_Mono } from 'next/font/google'

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Synarch Mission Control',
  description: 'Opaque Nexus Interface',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-noise">
        <div className="min-h-screen relative overflow-x-hidden">
          {/* Subtle ambient glows behind the glass */}
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-neon-cyan/10 blur-[120px] rounded-full pointer-events-none" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-neon-orange/10 blur-[100px] rounded-full pointer-events-none" />

          <main className="relative z-10 container mx-auto p-4 sm:p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
