import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono&display=swap" rel="stylesheet" />
      </Head>
      <body className="bg-elastic-blue-dark h-screen select-none">
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
