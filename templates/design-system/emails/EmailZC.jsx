/* Zooggies A/B — Wariant C: AUTORYTET + DOWÓD SPOŁECZNY ("ta sama nauka"), czysty/jasny */
function EmailZC() {
  return (
    <div>
      <ABMeta variant="C" subject="Ta sama nauka, której ufają tysiące — teraz dla psa"
        preheader="4,9/5 od opiekunów. Colostrum + kolagen od twórców Genactiv®." />
      <div className="em">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px 40px', borderBottom: '1px solid var(--ga-gray-150)' }}>
          <img src="../assets/logo-primary.png" alt="Genactiv" style={{ height: 28 }} />
        </div>

        <div className="em-pad" style={{ paddingBottom: 20 }}>
          <p className="em-eyebrow" style={{ color: '#C58A2E' }}>Powered by Genactiv® Colostrum</p>
          <h1 className="em-h1">Zaufały nam tysiące rodzin. <em>Teraz czas na pupile.</em></h1>
          <p className="em-body">Zooggies powstało na tej samej jakości i nauce, co produkty Genactiv®, którym zaufały tysiące ludzi. Opatentowane pozyskiwanie surowca i liofilizacja — colostrum i kolagen w pełni wierne naturze.</p>
        </div>

        {/* big rating / social proof */}
        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 20 }}>
          <div style={{ background: '#FBF1DF', borderRadius: 18, padding: '22px 24px', textAlign: 'center' }}>
            <div style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 36, color: 'var(--ga-ink)', lineHeight: 1 }}>4,9<span style={{ fontSize: 18, color: 'var(--ga-gray-500)' }}>/5</span></div>
            <div className="em-stars" style={{ fontSize: 18, margin: '6px 0' }}>★★★★★</div>
            <p style={{ fontSize: 13, fontStyle: 'italic', color: 'var(--ga-graphite)', margin: '6px auto 0', maxWidth: 360, lineHeight: 1.5 }}>„Mój pies wreszcie zjada wszystko z miski, a sierść lśni jak nigdy."</p>
            <p style={{ fontSize: 12, fontWeight: 700, color: '#C58A2E', margin: '8px 0 0' }}>— opiekunka, opinia zweryfikowana</p>
          </div>
        </div>

        {/* ingredient chips */}
        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 22 }}>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            {['Colostrum bovinum', 'Kolagen', 'Bez zbędnych dodatków'].map((t) => (
              <span key={t} style={{ border: '1.5px solid var(--ga-gray-300)', borderRadius: 999, padding: '8px 14px', fontSize: 12, fontWeight: 600, color: 'var(--ga-graphite)' }}>{t}</span>
            ))}
          </div>
        </div>

        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
          <div className="em-prod" style={{ background: '#FBF1DF' }}>
            <img className="em-prod__img" src="../assets/photo-zooggies.jpg" alt="" style={{ background: '#E9B872' }} />
            <div style={{ flex: 1 }}>
              <p className="em-prod__name">Zooggies dla psów</p>
              <p className="em-prod__meta">Colostrum + kolagen · dosmaczacz</p>
              <p className="em-prod__price">64,00 zł</p>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: 22 }}>
            <a className="em-btn em-btn--full" href="#" style={{ background: '#D69A3A', color: '#fff', boxShadow: '0 8px 20px rgba(214,154,58,.32)' }}>Zobacz Zooggies&nbsp;&nbsp;→</a>
          </div>
        </div>

        <EmailFooter />
      </div>
    </div>
  );
}
window.EmailZC = EmailZC;
