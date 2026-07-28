/* BEZ ZAKUPU · Krok 1 — Powitanie + kod rabatowy na 1. zakup */

function NurStep1A() {
  return (
    <div className="em">
      <Preheader text="Witaj w Genactiv® — masz −15% na pierwszy zakup 💪" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={1} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Witaj w Genactiv®</p>
        <h1 className="em-h1">Twój <em>−15%</em> na start</h1>
        <p className="em-body">Cześć! Miło, że tu jesteś. Na dobry początek mamy dla Ciebie rabat na pierwsze zamówienie <strong>Colostrum nr 1 w aptekach w Polsce</strong>.</p>
        <div style={{ marginTop: 22 }}><CodeBox /></div>
        <div style={{ marginTop: 20 }}>
          <ProductCard name="Colostrum Genactiv, kapsułki" meta="Suplement diety · 60 kapsułek" reviews={412} price="69,00 zł" />
        </div>
        <div style={{ textAlign: 'center', marginTop: 22 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Kup teraz z rabatem&nbsp;&nbsp;→</a>
        </div>
        <div style={{ marginTop: 20 }}><ShipNudge /></div>
      </div>
      <BenefitsBlock />
      <EmailFooter />
    </div>
  );
}

function NurStep1B() {
  return (
    <div className="em">
      <Preheader text="Zacznij swój plan na zdrowie — taniej o 15% ❤️" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={1} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Miło Cię poznać</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Zacznij swój plan na zdrowie — <em>taniej o 15%.</em></h1>
        <p className="em-body onb-narrow">Dziękujemy, że dołączyłaś. Oto Twój kod powitalny na pierwsze odkrycie colostrum Genactiv®.</p>
      </div>
      <div style={{ padding: '22px 40px 0' }}><CodeBox /></div>
      <div style={{ padding: '22px 40px 0' }}>
        <div style={{ background: 'var(--ga-red)', borderRadius: 22, padding: 22, textAlign: 'center' }}>
          <img src="../assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" style={{ width: 230, height: 'auto', margin: '0 auto' }} />
        </div>
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Odkryj Colostrum</a>
      </div>
      <TrustLine />
      <EmailFooter light />
    </div>
  );
}

window.NurStep1A = NurStep1A; window.NurStep1B = NurStep1B;
