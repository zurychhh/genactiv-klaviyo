/* PO ZAKUPIE · Krok 1 — Powitanie + potwierdzenie dobrego wyboru */

function PurStep1A() {
  return (
    <div className="em">
      <Preheader text="Zamówienie przyjęte — witaj w planie na zdrowie 💪" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 24 }}>
        <StepRail step={1} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Witaj w Genactiv®</p>
        <h1 className="em-h1">Dobry wybór, <em>Aniu!</em></h1>
        <p className="em-body">Dziękujemy za zaufanie. Właśnie dołączyłaś do tysięcy rodzin, które codziennie wspierają odporność z <strong>Colostrum nr 1 w aptekach</strong>. Twoje zamówienie jest już w drodze — a my pomożemy Ci wycisnąć z niego maksimum.</p>
        <div style={{ marginTop: 22 }}><OrderStrip /></div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Poznaj swój plan na zdrowie&nbsp;&nbsp;→</a>
        </div>
      </div>
      <BenefitsBlock />
      <EmailFooter />
    </div>
  );
}

function PurStep1B() {
  return (
    <div className="em">
      <Preheader text="Twój plan na zdrowie właśnie się zaczął ❤️" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 6px' }} className="onb-c">
        <StepRail step={1} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Cieszymy się, że tu jesteś</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Twój plan na zdrowie <em>właśnie się zaczął.</em></h1>
        <p className="em-body onb-narrow">Cześć Aniu, dziękujemy za pierwszy zakup. Zanim paczka dotrze, pokażemy Ci, jak najlepiej korzystać z Colostrum — krok po kroku.</p>
      </div>
      <div style={{ padding: '24px 40px 0' }}>
        <div style={{ background: 'var(--ga-red)', borderRadius: 22, padding: 22, textAlign: 'center' }}>
          <img src="../assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" style={{ width: 230, height: 'auto', margin: '0 auto' }} />
        </div>
      </div>
      <div style={{ padding: '26px 40px 4px' }}>
        <Ritual items={[
          { t: 'Odstaw w widocznym miejscu', d: 'Najlepiej blisko porannej kawy — łatwiej o regularność.' },
          { t: 'Weź pierwszą porcję jutro rano', d: 'Na czczo, popij wodą. Szczegóły w kolejnym mailu.' },
          { t: 'Daj naturze rytm', d: 'Pierwsze efekty zwykle po kilku tygodniach systematyczności.' },
        ]} />
      </div>
      <div className="onb-c" style={{ padding: '26px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Zacznij swój plan</a>
      </div>
      <TrustLine />
      <EmailFooter light />
    </div>
  );
}

window.PurStep1A = PurStep1A; window.PurStep1B = PurStep1B;
