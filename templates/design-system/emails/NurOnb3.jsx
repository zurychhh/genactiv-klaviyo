/* BEZ ZAKUPU · Krok 3 — Dowód społeczny (nr 1, opinie, eksperci) */

function NurStep3A() {
  return (
    <div className="em">
      <Preheader text="Nr 1 w aptekach w Polsce — zaufały nam tysiące rodzin" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={3} />
        <p className="em-eyebrow" style={{ marginTop: 18 }}>Zaufały nam tysiące</p>
        <h1 className="em-h1">Nr 1 <em>w aptekach</em> w Polsce</h1>
        <p className="em-body">Nie wierz nam na słowo. Colostrum Genactiv® to <strong>najczęściej wybierane colostrum w polskich aptekach</strong> w kategorii odporność.*</p>
        <div style={{ textAlign: 'center', margin: '22px 0' }}><Badge1 /></div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <ReviewTile txt="Stosuję cała rodzina przez całą jesień. Wreszcie spokojny sezon — polecam każdej mamie!" who="Karolina · zweryfikowany zakup" />
          <ReviewTile txt="Kapsułki łatwe do połknięcia, jakość czuć od pierwszego opakowania. Zamawiam ponownie." who="Tomasz · zweryfikowany zakup" />
        </div>
        <div style={{ marginTop: 22 }}><ExpertsRow /></div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Sprawdź, dlaczego nr 1&nbsp;&nbsp;→</a>
        </div>
        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--ga-gray-500)', margin: '14px 0 0' }}>*wg IQVIA, kategoria odporność, MAT 12/2024. Kod <strong style={{ color: 'var(--ga-ink)' }}>START15</strong> wciąż aktywny.</p>
      </div>
      <EmailFooter />
    </div>
  );
}

function NurStep3B() {
  return (
    <div className="em">
      <Preheader text="Wreszcie spokojny sezon — opinie polskich rodzin" />
      <HeaderLight />
      <div style={{ padding: '36px 40px 10px' }} className="onb-c">
        <StepRail step={3} center />
        <div className="em-stars" style={{ fontSize: 18, marginTop: 18 }}>★★★★★</div>
        <p className="onb-pull" style={{ maxWidth: 440, margin: '14px auto 0' }}>„Stosuje <em>cała rodzina</em> — wreszcie spokojny sezon.”</p>
        <p style={{ fontSize: 12, fontWeight: 700, letterSpacing: '.04em', textTransform: 'uppercase', color: 'var(--ga-gray-500)', margin: '16px 0 0' }}>Karolina · zweryfikowany zakup</p>
      </div>
      <div style={{ padding: '24px 40px 6px' }}>
        <div style={{ borderTop: '1px solid var(--ga-gray-150)', borderBottom: '1px solid var(--ga-gray-150)', padding: '20px 0', textAlign: 'center' }}>
          <Badge1 />
          <p style={{ fontSize: 11, color: 'var(--ga-gray-500)', margin: '12px 0 0' }}>wg IQVIA, kategoria odporność, MAT 12/2024</p>
        </div>
      </div>
      <div style={{ padding: '20px 40px 4px' }}><ExpertsRow /></div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--red" href="#">Dołącz do nich</a>
      </div>
      <EmailFooter light />
    </div>
  );
}

window.NurStep3A = NurStep3A; window.NurStep3B = NurStep3B;
