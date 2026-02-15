/**
 * Main application layout
 */
import Head from 'next/head';
import '../styles/globals.css';

export default function App({ Component, pageProps }) {
    return (
        <>
            <Head>
                <title>Pocket Option Live Market Pairs</title>
                <meta name="description" content="Real-time market pairs and price data from Pocket Option" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            <Component {...pageProps} />
        </>
    );
}
