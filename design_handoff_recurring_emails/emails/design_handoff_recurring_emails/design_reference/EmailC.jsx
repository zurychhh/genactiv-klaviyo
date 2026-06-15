/* Email C — editorial / minimal, cream, calm-premium */
function EmailC() {
  return (
    <div className="em" style={{ background: 'var(--ga-cream)' }}>
      <Preheader text="Twój plan na zdrowie nie lubi przerw — uzupełnij zapas" />

      {/* centered small logo */}
      <div style={{ textAlign: 'center', padding: '30px 40px 8px' }}>
        <img src="assets/logo-primary.png" alt="Genactiv" style={{ height: 26, margin: '0 auto' }} />
      </div>

      {/* product hero on rounded card */}
      <div style={{ padding: '20px 56px 0' }}>
        <div style={{ borderRadius: 24, overflow: 'hidden', background: 'var(--ga-red)', boxShadow: '0 18px 44px rgba(28,27,27,.14)' }}>
          <img src="assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" style={{ width: '100%', aspectRatio: '1 / 1', objectFit: 'cover' }} />
        </div>
      </div>

      {/* message */}
      <div style={{ padding: '34px 56px 8px', textAlign: 'center' }}>
        <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 12, letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--ga-red)', margin: '0 0 16px' }}>Czas na uzupełnienie</p>
        <h1 style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 32, lineHeight: 1.14, letterSpacing: '-.01em', margin: 0, color: 'var(--ga-ink)' }}>Twój plan na zdrowie<br /><em style={{ fontStyle: 'italic' }}>nie lubi przerw.</em></h1>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--ga-gray-700)', margin: '18px auto 0', maxWidth: 360 }}>Opakowanie powoli się kończy. Zadbaj o płynną ciągłość — czyste, nieprzetworzone colostrum, wierne naturze, dzień po dniu.</p>
        <div style={{ marginTop: 28 }}>
          <a className="em-btn em-btn--red" href="#">Uzupełnij zapas</a>
        </div>
      </div>

      {/* trust line */}
      <div style={{ padding: '30px 56px 36px', textAlign: 'center' }}>
        <div style={{ borderTop: '1px solid var(--ga-gray-300)', paddingTop: 24 }}>
          <div className="em-stars" style={{ fontSize: 16 }}>★★★★★</div>
          <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 13, letterSpacing: '.04em', color: 'var(--ga-graphite)', margin: '10px 0 0' }}>COLOSTRUM NR 1 W APTEKACH W POLSCE</p>
          <p style={{ fontSize: 11, color: 'var(--ga-gray-500)', margin: '4px 0 0' }}>na odporność* · zaufały nam tysiące rodzin</p>
        </div>
      </div>

      <EmailFooter light />
    </div>
  );
}
window.EmailC = EmailC;
