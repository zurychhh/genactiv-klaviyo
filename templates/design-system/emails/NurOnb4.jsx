/* BEZ ZAKUPU · Krok 4 — Przypomnienie o kodzie / oferta (urgency) */

function NurStep4A() {
  return (
    <div className="em">
      <Preheader text="Twój kod −15% wygasa za 48 godzin" />
      <UrgBar>Twój kod <b>−15%</b> wygasa za 48 godzin</UrgBar>
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={4} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Nie przegap</p>
        <h1 className="em-h1">Twój kod <em>wciąż czeka</em></h1>
        <p className="em-body">Zostawiłaś go bez użycia — a szkoda. <strong>START15</strong> to −15% na pierwsze odkrycie Colostrum nr 1 w aptekach. Ale tylko przez najbliższe <strong>48 godzin</strong>.</p>
        <div style={{ marginTop: 22 }}><CodeBox sub="−15% na cały koszyk · ważny jeszcze 48h" /></div>
        <div style={{ marginTop: 20 }}>
          <ProductCard name="Colostrum Genactiv, kapsułki" meta="Bestseller · 60 kapsułek" reviews={412} price="58,65 zł" old="69,00 zł" />
        </div>
        <div style={{ textAlign: 'center', marginTop: 22 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Wykorzystaj kod teraz&nbsp;&nbsp;→</a>
        </div>
        <div style={{ marginTop: 20 }}><ShipNudge /></div>
      </div>
      <EmailFooter />
    </div>
  );
}

function NurStep4B() {
  return (
    <div className="em">
      <Preheader text="Delikatne przypomnienie — Twój plan wciąż czeka" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={4} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Delikatne przypomnienie</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Twój plan na zdrowie wciąż <em>czeka.</em></h1>
        <p className="em-body onb-narrow">Bez pośpiechu — ale Twój kod powitalny ma swój termin. Skorzystaj, zanim wygaśnie.</p>
      </div>
      <div style={{ padding: '22px 40px 0' }}><CodeBox sub="−15% · ważny jeszcze 48 godzin" /></div>
      <div style={{ padding: '22px 40px 0' }}>
        <div style={{ background: 'var(--ga-red)', borderRadius: 22, padding: 22, textAlign: 'center' }}>
          <img src="../assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" style={{ width: 220, height: 'auto', margin: '0 auto' }} />
        </div>
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Zacznij teraz z −15%</a>
      </div>
      <TrustLine />
      <EmailFooter light />
    </div>
  );
}

window.NurStep4A = NurStep4A; window.NurStep4B = NurStep4B;
