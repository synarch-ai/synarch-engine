import './globals.css'

export const metadata = {
  title: 'Synarch Mission Control',
  description: 'Real-time Mission Control for the Synarch autonomous agent engine',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
