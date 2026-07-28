/* Cross-sell 1 — Colostrum → Fiberbiom (synergia odporność + jelita), pink */
function EmailCS1() {
  return (
    <div className="em">
      <Preheader text="Zadbałaś o odporność — czas na jelita. Poznaj Fiberbiom 💕" />

      {/* pink header */}
      <div style={{ background: 'var(--ga-pink)', padding: '22px 40px', textAlign: 'center' }}>
        <img src="../assets/logo-white.png" alt="Genactiv" style={{ height: 30, margin: '0 auto' }} />
      </div>

      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <p className="em-eyebrow" style={{ color: 'var(--ga-pink)' }}>Dopełnij swoją rutynę</p>
        <h1 className="em-h1">Twoja odporność ma <em>nowego sojusznika.</em></h1>
        <p className="em-body">Skoro dbasz o odporność z Genactiv® Colostrum — czas na jelita. To od nich zależy Twoja odporność i energia. <strong>Fiberbiom</strong> łączy rozpuszczalny błonnik z kory modrzewia i to samo Colostrum, które już znasz.</p>
      </div>

      {/* synergy duo */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, background: 'var(--ga-pink-soft)', borderRadius: 18, padding: '22px 18px' }}>
          <div style={{ textAlign: 'center' }}>
            <img src="../assets/photo-colostrum-nr1.png" alt="" style={{ width: 78, height: 78, borderRadius: 999, objectFit: 'cover', background: 'var(--ga-red)', margin: '0 auto' }} />
            <p style={{ fontSize: 11, fontWeight: 700, color: 'var(--ga-graphite)', margin: '8px 0 0' }}>Odporność</p>
          </div>
          <span style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 26, color: 'var(--ga-pink)' }}>+</span>
          <div style={{ textAlign: 'center' }}>
            <img src="../assets/photo-fiberbiom.jpg" alt="" style={{ width: 78, height: 78, borderRadius: 999, objectFit: 'cover', background: 'var(--ga-pink)', margin: '0 auto' }} />
            <p style={{ fontSize: 11, fontWeight: 700, color: 'var(--ga-graphite)', margin: '8px 0 0' }}>Jelita</p>
          </div>
          <span style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 26, color: 'var(--ga-pink)' }}>=</span>
          <div style={{ textAlign: 'center', maxWidth: 96 }}>
            <div style={{ width: 78, height: 78, borderRadius: 999, background: 'var(--ga-pink)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
              <EIcon name="heart" size={34} color="#fff" fill="#fff" />
            </div>
            <p style={{ fontSize: 11, fontWeight: 700, color: 'var(--ga-graphite)', margin: '8px 0 0' }}>Synergia</p>
          </div>
        </div>
      </div>

      {/* product card */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
        <div className="em-prod">
          <img className="em-prod__img" src="../assets/photo-fiberbiom.jpg" alt="" style={{ background: 'var(--ga-pink)' }} />
          <div style={{ flex: 1 }}>
            <p className="em-prod__name">Genactiv® Fiberbiom</p>
            <p className="em-prod__meta">Błonnik + Colostrum · 15 saszetek</p>
            <div className="em-stars" style={{ margin: '7px 0 0' }}>★★★★★ <span style={{ color: 'var(--ga-gray-500)', fontSize: 12 }}>(88)</span></div>
            <p className="em-prod__price"><s>99,00 zł</s>89,00 zł</p>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: 22 }}>
          <a className="em-btn em-btn--pink em-btn--full" href="#">Poznaj Fiberbiom&nbsp;&nbsp;→</a>
        </div>
      </div>

      {/* bundle nudge */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 32 }}>
        <div className="em-ship" style={{ background: 'var(--ga-pink-soft)' }}>
          <EIcon name="refresh" size={22} color="var(--ga-pink)" />
          <span className="em-ship__txt">Dorzuć Fiberbiom do kolejnego zamówienia Colostrum i&nbsp;złap <strong>darmową dostawę</strong>.</span>
        </div>
      </div>

      <EmailFooter />
    </div>
  );
}
window.EmailCS1 = EmailCS1;
