/* PO ZAKUPIE · Krok 4 — Cross-sell: Fiberbiom (synergia z colostrum) */

function PurStep4A() {
  return (
    <div className="em">
      <Preheader text="Colostrum dba o odporność. Czas zadbać o jelita 😍" />
      <HeaderRed />
      <div className="em-pad" style={{ paddingBottom: 22 }}>
        <StepRail step={4} />
        <p className="em-eyebrow" style={{ marginTop: 18, color: 'var(--ga-pink)' }}>Twój następny krok</p>
        <h1 className="em-h1">Dodaj <em>rytm</em> swoim jelitom</h1>
        <p className="em-body">Colostrum buduje Twoją odporność. <strong>Fiberbiom</strong> idzie krok dalej — łączy rozpuszczalny błonnik z kory modrzewia z Genactiv® Colostrum, by zadbać o mikrobiom i barierę jelitową.</p>
        <div style={{ marginTop: 20 }}>
          <ProductCard img="photo-fiberbiom.jpg" bg="var(--ga-pink)" name="Genactiv® Fiberbiom" meta="Błonnik + colostrum · 30 saszetek" reviews={128} price="79,00 zł" old="92,00 zł" />
        </div>
        <div style={{ marginTop: 16 }}>
          <div className="onb-synergy">
            <EIcon name="refresh" size={22} color="var(--ga-pink)" />
            <span><strong>−15% w zestawie z Colostrum.</strong> Synergia dwóch składników aktywnych w jednym planie.</span>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--pink em-btn--full" href="#">Dodaj Fiberbiom do planu&nbsp;&nbsp;→</a>
        </div>
      </div>
      <EmailFooter />
    </div>
  );
}

function PurStep4B() {
  return (
    <div className="em">
      <Preheader text="Lekkość błonnika. Moc colostrum." />
      <HeaderLight />
      <div style={{ padding: '34px 40px 8px' }} className="onb-c">
        <StepRail step={4} center />
        <p className="em-eyebrow" style={{ marginTop: 18, color: 'var(--ga-pink)' }}>Poznaj Fiberbiom</p>
        <h1 className="em-h1" style={{ maxWidth: 430, margin: '0 auto' }}>Lekkość błonnika. <em>Moc colostrum.</em></h1>
        <p className="em-body onb-narrow">Naturalne uzupełnienie Twojego planu. Fiberbiom łączy błonnik z kory modrzewia z Genactiv® Colostrum — dla jelit, które łapią rytm.</p>
      </div>
      <div style={{ padding: '24px 40px 0' }}>
        <div style={{ background: 'var(--ga-pink)', borderRadius: 22, padding: 22, textAlign: 'center' }}>
          <img src="../assets/photo-fiberbiom.jpg" alt="Genactiv Fiberbiom" style={{ width: '100%', maxWidth: 420, height: 220, objectFit: 'cover', borderRadius: 14, margin: '0 auto' }} />
        </div>
      </div>
      <div style={{ padding: '24px 40px 4px' }}>
        <ReasonList items={[
          { icon: 'refresh', t: 'Wspiera mikrobiom', d: 'Rozpuszczalny błonnik karmi dobre bakterie jelitowe.' },
          { icon: 'check', t: 'Dba o barierę jelitową', d: 'Colostrum naturalnie wspiera śluzówkę jelit.' },
          { icon: 'heart', t: 'Lekkość każdego dnia', d: 'Delikatna formuła do codziennego stosowania.' },
        ]} />
      </div>
      <div className="onb-c" style={{ padding: '24px 40px 30px' }}>
        <a className="em-btn em-btn--pink" href="#">Poznaj Fiberbiom</a>
      </div>
      <EmailFooter light />
    </div>
  );
}

window.PurStep4A = PurStep4A; window.PurStep4B = PurStep4B;
