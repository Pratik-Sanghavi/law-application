export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body
        style={{
          fontFamily: "Arial",
          maxWidth: 900,
          margin: "40px auto",
          padding: 20,
        }}
      >
        {children}
      </body>
    </html>
  );
}
