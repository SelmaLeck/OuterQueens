import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {title:'OuterQueens',description:'Minecraft Bauprojekt, Farmen und Team-Fortschritt'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="de"><body>{children}</body></html>}
