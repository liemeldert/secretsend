"use client"
import { MantineProvider } from '@mantine/core';
import { FooterLinks } from './components/footer';
import { SiteHeader } from './components/header';


const footerData = [
  {
    title: 'Links',
    links: [
      { label: 'Home', link: '/' },
      // { label: 'Decrypt Password', link: '/careers' },
      // { label: 'Embed us', link: '/contact' },
    ],
  },
];


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>PWSend</title>
      </head>
      <body>
        <MantineProvider withGlobalStyles withNormalizeCSS>
          <SiteHeader />
          {children}
          <FooterLinks data={footerData}/>
        </MantineProvider>
        
      </body>
    </html>
  );
}