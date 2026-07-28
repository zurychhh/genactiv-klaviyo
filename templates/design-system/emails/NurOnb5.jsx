/* BEZ ZAKUPU · Krok 5 — Ostatnie wołanie (last call) */

function NurStep5A() {
  return (
    <div className="em">
      <Preheader text="Ostatnia szansa — kod −15% znika dziś o północy" />
      <UrgBar>Ostatnia szansa — kod znika <b>dziś o północy</b></UrgBar>
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={5} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Ostatnie wołanie</p>
        <h1 className="em-h1">Kod <em>−15%</em> znika dziś</h1>
        <p className="em-body">To już naprawdę ostatni moment. Po północy <strong>START15</strong> przestaje działać. Zacznij swój plan na zdrowie z najlepszym colostrum w polskich aptekach — w najlepszej cenie.</p>
        <div style={{ marginTop: 22 }}><CodeBox sub="−15% · wygasa dziś o 23:59" /></div>
        <div style={{ marginTop: 20 }}>
          <ProductCard name="Pakiet startowy Colostrum" meta="Bestseller · 60 kapsułek + poradnik" reviews={412} price="58,65 zł" old="69,00 zł" />
        </div>
        <div style={{ textAlign: 'center', marginTop: 22 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Odbierz rabat, zanim zniknie&nbsp;&nbsp;→</a>
        </div>
        <div style={{ marginTop: 20 }}><ShipNudge /></div>
      </div>
      <EmailFooter />
    </div>
  );
}

function NurStep5B() {
  return (
    <div className="em">
      <Preheader text="Ostatnie przypomnienie — kod ważny do północy" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={5} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Ostatnie przypomnienie</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Zostawiamy to <em>w Twoich rękach.</em></h1>
        <p className="em-body onb-narrow">Nie chcemy naciskać. Ale Twój kod powitalny wygasa dziś o północy — a dobre nawyki najlepiej zaczynać od dziś.</p>
      </div>
      <div style={{ padding: '22px 40px 0' }}>
        <div style={{ background: 'var(--ga-cream)', borderRadius: 22, padding: 22, textAlign: 'center' }}>
          <img src="../assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" style={{ width: 210, height: 'auto', margin: '0 auto' }} />
          <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 17, color: 'var(--ga-ink)', margin: '14px 0 0' }}>Colostrum Genactiv, kapsułki</p>
          <p style={{ fontSize: 13, color: 'var(--ga-gray-700)', margin: '4px 0 0' }}><s style={{ color: 'var(--ga-gray-500)' }}>69,00 zł</s> &nbsp;58,65 zł z kodem START15</p>
        </div>
      </div>
      <div style={{ padding: '20px 40px 0' }}><CodeBox label="Twój kod (wygasa dziś)" sub="−15% · do 23:59" /></div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Skorzystaj z −15%</a>
      </div>
      <TrustLine />
      <EmailFooter light />
    </div>
  );
}

window.NurStep5A = NurStep5A; window.NurStep5B = NurStep5B;
