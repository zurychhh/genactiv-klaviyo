/* PO ZAKUPIE · Krok 2 — Jak stosować (dawkowanie, rytuał, kiedy efekty) */

function PurStep2A() {
  return (
    <div className="em">
      <Preheader text="3 proste kroki, by Colostrum działało najlepiej" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={2} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Jak stosować</p>
        <h1 className="em-h1">Twój rytuał z <em>Colostrum</em></h1>
        <p className="em-body">To naprawdę proste. Najważniejsza jest <strong>regularność</strong> — bo natura lubi rytm. Oto jak włączyć Colostrum w swój dzień:</p>
        <div style={{ background: 'var(--ga-cream)', borderRadius: 16, padding: '18px 20px', marginTop: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 14, textAlign: 'center' }}>
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 22, color: 'var(--ga-red)' }}>1–2</p>
              <p style={{ margin: '2px 0 0', fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--ga-graphite)' }}>kapsułki dziennie</p>
            </div>
            <div style={{ width: 1, background: 'var(--ga-gray-300)' }} />
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 22, color: 'var(--ga-red)' }}>Rano</p>
              <p style={{ margin: '2px 0 0', fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--ga-graphite)' }}>na czczo</p>
            </div>
            <div style={{ width: 1, background: 'var(--ga-gray-300)' }} />
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 22, color: 'var(--ga-red)' }}>Woda</p>
              <p style={{ margin: '2px 0 0', fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--ga-graphite)' }}>popij chłodną</p>
            </div>
          </div>
        </div>
        <div style={{ marginTop: 22 }}>
          <Ritual items={[
            { t: 'Rano, zanim zjesz', d: 'Pusty żołądek = lepsze przyswajanie cennych składników colostrum.' },
            { t: 'Popij chłodną wodą', d: 'Unikaj gorących napojów — wysoka temperatura nie służy aktywnym składnikom.' },
            { t: 'Codziennie, bez przerw', d: 'Systematyczność przez min. 4–8 tygodni daje najlepszy efekt.' },
          ]} />
        </div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Zobacz pełny poradnik stosowania&nbsp;&nbsp;→</a>
        </div>
      </div>
      <EmailFooter />
    </div>
  );
}

function PurStep2B() {
  return (
    <div className="em">
      <Preheader text="Najlepsze efekty lubią rytm — oto Twój poranny rytuał" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={2} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Twój poranny rytuał</p>
        <h1 className="em-h1" style={{ maxWidth: 420, margin: '0 auto' }}>Najlepsze efekty lubią <em>rytm.</em></h1>
        <p className="em-body onb-narrow">Colostrum nie potrzebuje wiele — potrzebuje regularności. Trzy spokojne kroki, które wystarczy powtarzać każdego ranka.</p>
      </div>
      <div style={{ padding: '24px 40px 6px' }}>
        <Ritual items={[
          { t: 'Obudź się i nawodnij', d: 'Szklanka wody na dobry początek dnia.' },
          { t: '1–2 kapsułki na czczo', d: 'Zanim sięgniesz po śniadanie — popij chłodną wodą.' },
          { t: 'Powtarzaj codziennie', d: 'Po kilku tygodniach rytm stanie się nawykiem.' },
        ]} />
      </div>
      <div style={{ padding: '22px 40px 4px' }}>
        <ExpertQuote quote="Colostrum działa najlepiej, gdy stosujemy je systematycznie. To nie kuracja na kilka dni — to element codziennego planu na zdrowie." />
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Pełny poradnik stosowania</a>
      </div>
      <EmailFooter light />
    </div>
  );
}

window.PurStep2A = PurStep2A; window.PurStep2B = PurStep2B;
