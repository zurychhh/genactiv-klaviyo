/* BEZ ZAKUPU · Krok 2 — Dlaczego colostrum (edukacja, problem → rozwiązanie) */

function NurStep2A() {
  return (
    <div className="em">
      <Preheader text="250 aktywnych składników w jednej substancji" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={2} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Poznaj składnik</p>
        <h1 className="em-h1">Dlaczego <em>colostrum?</em></h1>
        <p className="em-body">To pierwszy pokarm natury — <strong>250 aktywnych składników w jednej substancji</strong>. Czyste, nieprzetworzone, w 100% wierne naturze. Oto dlaczego działa:</p>
        <div style={{ marginTop: 22 }}>
          <ReasonList items={[
            { icon: 'check', t: 'Immunoglobuliny', d: 'Naturalne przeciwciała wspierające odporność każdego dnia.' },
            { icon: 'heart', t: 'Laktoferyna', d: 'Białko o właściwościach wspierających naturalną barierę organizmu.' },
            { icon: 'refresh', t: 'Czystość i natura', d: 'Liofilizowane colostrum bez zbędnych dodatków — moc w czystej formie.' },
          ]} />
        </div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Dowiedz się więcej&nbsp;&nbsp;→</a>
        </div>
        <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--ga-gray-500)', margin: '14px 0 0' }}>Pamiętaj — masz <strong style={{ color: 'var(--ga-red)' }}>−15%</strong> z kodem <strong style={{ color: 'var(--ga-ink)' }}>START15</strong>.</p>
      </div>
      <BenefitsBlock />
      <EmailFooter />
    </div>
  );
}

function NurStep2B() {
  return (
    <div className="em">
      <Preheader text="Natura + nauka. Czym właściwie jest colostrum?" />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={2} center />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Natura + nauka</p>
        <h1 className="em-h1" style={{ maxWidth: 420, margin: '0 auto' }}>Co to jest <em>colostrum?</em></h1>
        <p className="em-body onb-narrow">Colostrum (siara) to pierwszy pokarm, jaki natura przygotowuje dla noworodka — bogaty w składniki wspierające odporność od pierwszych chwil życia.</p>
      </div>
      <div style={{ padding: '24px 40px 4px' }}>
        <ExpertQuote img="expert-halasa.png" name="dr hab. n. med. Hałasa" role="Immunolog" quote="Colostrum bovinum to jedno z najlepiej przebadanych naturalnych źródeł immunoglobulin. To natura wsparta nauką." />
      </div>
      <div style={{ padding: '22px 40px 4px' }}>
        <ReasonList items={[
          { icon: 'check', t: '250 aktywnych składników', d: 'W jednej, naturalnej substancji.' },
          { icon: 'refresh', t: 'Liofilizacja', d: 'Delikatny proces, który zachowuje to, co najcenniejsze.' },
        ]} />
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Czytaj o colostrum</a>
      </div>
      <EmailFooter light />
    </div>
  );
}

window.NurStep2A = NurStep2A; window.NurStep2B = NurStep2B;
