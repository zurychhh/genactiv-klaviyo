/* PO ZAKUPIE · Krok 3 — Czego się spodziewać (timeline efektów) */

const PUR3_TL = [
  { when: 'Tydzień 1–2', t: 'Budujesz rytm', d: 'Organizm przyzwyczaja się do codziennej porcji. Najważniejszy etap — nie odpuszczaj.' },
  { when: 'Tydzień 3–4', t: 'Pierwsze sygnały', d: 'Wiele osób zauważa lepsze samopoczucie i więcej energii w ciągu dnia.' },
  { when: 'Tydzień 6–8', t: 'Pełna moc planu', d: 'Wsparcie odporności działa najlepiej przy konsekwencji. To Twój nowy standard.' },
];

function PurStep3A() {
  return (
    <div className="em">
      <Preheader text="Twoje 8 tygodni z Colostrum — czego się spodziewać" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={3} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Czego się spodziewać</p>
        <h1 className="em-h1">Twoje 8 tygodni z <em>Colostrum</em></h1>
        <p className="em-body">Natura potrzebuje czasu i rytmu. Oto jak zwykle wygląda droga, gdy stosujesz Colostrum systematycznie — krok po kroku.</p>
        <div style={{ marginTop: 24 }}><Timeline items={PUR3_TL} /></div>
        <div style={{ marginTop: 22 }}>
          <ExpertQuote img="expert-halasa.png" name="dr hab. n. med. Hałasa" role="Immunolog" quote="Colostrum to naturalne wsparcie bariery odpornościowej. Kluczem jest regularność — efekty budują się tygodniami, nie dniami." />
        </div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Dowiedz się więcej o colostrum&nbsp;&nbsp;→</a>
        </div>
      </div>
      <EmailFooter />
    </div>
  );
}

function PurStep3B() {
  return (
    <div className="em">
      <Preheader text="Natura potrzebuje rytmu — daj jej czas" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={3} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Cierpliwość się opłaca</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Natura potrzebuje <em>rytmu.</em></h1>
        <p className="em-body onb-narrow">Nie szukaj efektów po dwóch dniach. Prawdziwa zmiana w odporności buduje się tygodniami — i właśnie dlatego warto.</p>
      </div>
      <div style={{ padding: '26px 40px 6px' }}><Timeline items={PUR3_TL} /></div>
      <div style={{ padding: '20px 40px 4px' }}>
        <div style={{ background: 'var(--ga-cream)', borderRadius: 16, padding: '18px 20px', textAlign: 'center' }}>
          <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: 'var(--ga-graphite)' }}>Wskazówka: zaznacz w kalendarzu datę za 4 tygodnie. To moment, w którym najczęściej widać pierwsze efekty. ❤️</p>
        </div>
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Poznaj naukę o colostrum</a>
      </div>
      <EmailFooter light />
    </div>
  );
}

window.PurStep3A = PurStep3A; window.PurStep3B = PurStep3B;
