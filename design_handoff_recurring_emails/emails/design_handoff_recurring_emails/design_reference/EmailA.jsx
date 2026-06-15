/* Email A — "Kończy się Twoje Colostrum?" — warm urgency reminder, bold red */
function EmailA() {
  return (
    <div className="em">
      <Preheader text="Twój zapas dobiega końca — uzupełnij i nie trać rytmu 💪" />

      {/* red header */}
      <div style={{ background: 'var(--ga-red)', padding: '22px 40px', textAlign: 'center' }}>
        <img src="assets/logo-white.png" alt="Genactiv" style={{ height: 30, margin: '0 auto' }} />
      </div>

      {/* hero */}
      <div className="em-pad" style={{ paddingBottom: 24 }}>
        <p className="em-eyebrow">Pora uzupełnić zapas</p>
        <h1 className="em-h1">Kończy się Twoje <em>Colostrum?</em></h1>
        <p className="em-body">Cześć Aniu! Minął już prawie miesiąc od Twojego ostatniego zamówienia, więc opakowanie pewnie powoli się kończy. <strong>Nie rób przerwy w odporności</strong> — uzupełnij zapas, zanim zabraknie.</p>

        {/* supply meter */}
        <div style={{ background: 'var(--ga-cream)', borderRadius: 14, padding: '16px 18px', marginTop: 22 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 9 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--ga-graphite)' }}>Twój szacowany zapas</span>
            <span style={{ fontSize: 13, fontWeight: 800, color: 'var(--ga-red)' }}>~5 porcji</span>
          </div>
          <div style={{ height: 9, background: '#fff', borderRadius: 999, overflow: 'hidden' }}>
            <i style={{ display: 'block', height: '100%', width: '14%', background: 'var(--ga-red)' }} />
          </div>
        </div>
      </div>

      {/* product card + CTA */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
        <div className="em-prod">
          <img className="em-prod__img" src="assets/photo-colostrum-nr1.png" alt="" style={{ background: 'var(--ga-red)' }} />
          <div style={{ flex: 1 }}>
            <p className="em-prod__name">Colostrum Genactiv, kapsułki</p>
            <p className="em-prod__meta">Suplement diety · 60 kapsułek</p>
            <div className="em-stars" style={{ margin: '7px 0 0' }}>★★★★★ <span style={{ color: 'var(--ga-gray-500)', fontSize: 12 }}>(412)</span></div>
            <p className="em-prod__price">69,00 zł</p>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: 22 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Zamów ponownie&nbsp;&nbsp;→</a>
        </div>
      </div>

      {/* free shipping nudge */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 30 }}>
        <div className="em-ship">
          <EIcon name="truck" size={22} color="var(--ga-red)" />
          <span className="em-ship__txt">Dorzuć drugi produkt i&nbsp;masz <strong>darmową dostawę</strong> — od 99&nbsp;zł.</span>
        </div>
      </div>

      {/* benefits reminder */}
      <div style={{ background: 'var(--ga-gray-100)', padding: '28px 40px' }}>
        <p style={{ textAlign: 'center', fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 15, margin: '0 0 20px', letterSpacing: '.02em' }}>Za co pokochasz nasze Colostrum</p>
        <div className="em-benefits">
          <div className="em-benefit"><img src="assets/icon-smak.png" alt="" /><span>SMAK</span></div>
          <div className="em-benefit"><img src="assets/icon-naturalnosc.png" alt="" /><span>NATURALNOŚĆ</span></div>
          <div className="em-benefit"><img src="assets/icon-forma.png" alt="" /><span>FORMY PODANIA</span></div>
        </div>
      </div>

      <EmailFooter />
    </div>
  );
}
window.EmailA = EmailA;
