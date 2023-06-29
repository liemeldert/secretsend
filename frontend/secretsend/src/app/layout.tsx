"use client"
import { MantineProvider } from '@mantine/core';



export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
      </head>
      <body>
        <MantineProvider withGlobalStyles withNormalizeCSS>{children}</MantineProvider>
      </body>
    </html>
  );
}