/* PO ZAKUPIE · Krok 5 — Cała rodzina (cross-sell) + prośba o opinię */

const FAM_FULL = [
  { img: 'photo-fiberbiom.jpg', bg: 'var(--ga-pink)', name: 'Fiberbiom', desc: 'Błonnik + colostrum dla jelit i mikrobiomu.', cta: 'Odkryj' },
  { img: 'photo-dermo.webp', name: 'DERMO', desc: 'Kosmetyki z colostrum i mlekiem klaczy.', cta: 'Zobacz' },
  { img: 'photo-zooggies.jpg', name: 'Zooggies', desc: 'Colostrum + kolagen dla Twojego pupila.', cta: 'Poznaj' },
  { img: 'photo-colostrum-nr1.png', bg: 'var(--ga-red)', name: 'Colostrum Junior', desc: 'Polecane przez mamy, lubiane przez dzieci.', cta: 'Sprawdź' },
];

function ReviewNudge({ light }) {
  return (
    <div style={{ background: light ? 'var(--ga-cream)' : 'var(--ga-red-soft)', borderRadius: 16, padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 14 }}>
      <EIcon name="heart" size={24} color="var(--ga-red)" fill="var(--ga-red)" />
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 14, color: 'var(--ga-ink)' }}>Jak sprawdza się Twoje Colostrum?</p>
        <p style={{ margin: '3px 0 0', fontSize: 12.5, lineHeight: 1.45, color: 'var(--ga-gray-700)' }}>Podziel się opinią i pomóż innym rodzinom wybrać dobrze.</p>
      </div>
      <a className="onb-fam__lnk" href="#" style={{ whiteSpace: 'nowrap' }}>Dodaj opinię →</a>
    </div>
  );
}

function PurStep5A() {
  return (
    <div className="em">
      <Preheader text="Twój plan na zdrowie rośnie — poznaj całą rodzinę Genactiv" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={5} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Twój plan rośnie</p>
        <h1 className="em-h1">Zdrowie <em>całej rodziny</em></h1>
        <p className="em-body">Colostrum to dopiero początek. Genactiv® to cały plan na zdrowie — dla Ciebie, Twoich bliskich, skóry, a nawet pupila.</p>
        <div style={{ marginTop: 22 }}><FamilyGrid items={FAM_FULL} /></div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Odkryj całą rodzinę Genactiv&nbsp;&nbsp;→</a>
        </div>
        <div style={{ marginTop: 22 }}><ReviewNudge /></div>
      </div>
      <EmailFooter />
    </div>
  );
}

function PurStep5B() {
  return (
    <div className="em">
      <Preheader text="Jeden plan. Całe zdrowie." />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={5} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Cała rodzina Genactiv</p>
        <h1 className="em-h1" style={{ maxWidth: 420, margin: '0 auto' }}>Jeden plan. <em>Całe zdrowie.</em></h1>
        <p className="em-body onb-narrow">Od odporności, przez jelita, po skórę i pupila — Genactiv® rośnie razem z Twoimi potrzebami.</p>
      </div>
      <div style={{ padding: '24px 40px 4px' }}>
        <FamilyGrid items={[FAM_FULL[1], FAM_FULL[2]]} />
      </div>
      <div className="onb-c" style={{ padding: '22px 40px 8px' }}>
        <a className="em-btn em-btn--red" href="#">Zobacz wszystkie linie</a>
      </div>
      <div style={{ padding: '14px 40px 30px' }}><ReviewNudge light /></div>
      <EmailFooter light />
    </div>
  );
}

window.PurStep5A = PurStep5A; window.PurStep5B = PurStep5B;
