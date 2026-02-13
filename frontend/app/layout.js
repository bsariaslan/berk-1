import './globals.css';

export const metadata = {
  title: 'Kredi Kartı Kampanya Karşılaştırma',
  description: 'Hangi kartınızla alışveriş yapmalısınız? En avantajlı kampanyayı bulun!',
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
