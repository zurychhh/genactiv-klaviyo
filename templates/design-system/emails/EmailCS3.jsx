/* Cross-sell 3 — Colostrum → DERMO (kosmetyki), editorial premium, krem/grafit */
function EmailCS3() {
  return (
    <div className="em" style={{ background: 'var(--ga-cream)' }}>
      <Preheader text="Zadbaj o skórę tak, jak o odporność — poznaj linię DERMO" />

      <div style={{ textAlign: 'center', padding: '30px 40px 6px' }}>
        <img src="../assets/logo-primary.png" alt="Genactiv" style={{ height: 26, margin: '0 auto' }} />
      </div>

      {/* product hero */}
      <div style={{ padding: '18px 56px 0' }}>
        <div style={{ borderRadius: 24, overflow: 'hidden', boxShadow: '0 18px 44px rgba(28,27,27,.14)' }}>
          <img src="../assets/photo-dermo.webp" alt="Genactiv DERMO" style={{ width: '100%', aspectRatio: '1 / 1', objectFit: 'cover' }} />
        </div>
      </div>

      <div style={{ padding: '32px 56px 8px', textAlign: 'center' }}>
        <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 12, letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--ga-red)', margin: '0 0 16px' }}>Linia DERMO</p>
        <h1 style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 32, lineHeight: 1.14, letterSpacing: '-.01em', margin: 0, color: 'var(--ga-ink)' }}>Od środka —<br /><em style={{ fontStyle: 'italic' }}>i na zewnątrz.</em></h1>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--ga-gray-700)', margin: '18px auto 0', maxWidth: 380 }}>To samo, w co już wierzysz — colostrum bovinum i mleko klaczy — teraz w kosmetykach. Synergia dwóch darów natury dla cery dojrzałej, problematycznej i podrażnionej.</p>
        <div style={{ marginTop: 26 }}>
          <a className="em-btn em-btn--red" href="#">Poznaj DERMO</a>
        </div>
      </div>

      {/* dual benefit */}
      <div style={{ padding: '28px 56px 36px' }}>
        <div style={{ borderTop: '1px solid var(--ga-gray-300)', paddingTop: 24, display: 'flex', gap: 28, justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', flex: 1 }}>
            <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 22, color: 'var(--ga-red)', margin: 0 }}>Colostrum</p>
            <p style={{ fontSize: 12, color: 'var(--ga-gray-500)', margin: '4px 0 0' }}>regeneracja i odżywienie</p>
          </div>
          <div style={{ width: 1, background: 'var(--ga-gray-300)' }} />
          <div style={{ textAlign: 'center', flex: 1 }}>
            <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 22, color: 'var(--ga-red)', margin: 0 }}>Mleko klaczy</p>
            <p style={{ fontSize: 12, color: 'var(--ga-gray-500)', margin: '4px 0 0' }}>kojenie i nawilżenie</p>
          </div>
        </div>
      </div>

      <EmailFooter light />
    </div>
  );
}
window.EmailCS3 = EmailCS3;
