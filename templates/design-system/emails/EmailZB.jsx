/* Zooggies A/B — Wariant B: PROBLEM → ROZWIĄZANIE ("niejadek"), produkt na złotym tle */
function EmailZB() {
  const bullets = [
    ['Smak, który zachęca', 'naturalny „dosmaczacz" — posyp karmę i gotowe'],
    ['Odporność', 'colostrum bovinum, to samo co w Genactiv®'],
    ['Stawy i sierść', 'kolagen wspierający kondycję pupila'],
  ];
  return (
    <div>
      <ABMeta variant="B" subject="Twój pies grymasi przy misce? 🐾"
        preheader="Posyp karmę Zooggies — i po kłopocie. Colostrum + kolagen." />
      <div className="em">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px 40px', borderBottom: '1px solid var(--ga-gray-150)' }}>
          <img src="../assets/logo-primary.png" alt="Genactiv" style={{ height: 28 }} />
        </div>

        {/* solid gold hero with product */}
        <div style={{ background: '#E9B872', padding: '34px 40px', textAlign: 'center' }}>
          <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 12, letterSpacing: '.16em', textTransform: 'uppercase', color: '#6b4a12', margin: '0 0 12px' }}>Koniec z grymaszeniem</p>
          <h1 style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 32, lineHeight: 1.1, color: '#3a2708', margin: '0 0 18px' }}>Niejadek przy misce?<br />Po prostu <em style={{ fontStyle: 'italic' }}>posyp.</em></h1>
          <img src="../assets/photo-zooggies.jpg" alt="Zooggies" style={{ width: 200, height: 200, objectFit: 'cover', borderRadius: 18, margin: '0 auto', boxShadow: '0 14px 30px rgba(58,39,8,.22)' }} />
        </div>

        <div className="em-pad" style={{ paddingBottom: 16 }}>
          <p className="em-body" style={{ marginTop: 0 }}>Zooggies to suplement i „dosmaczacz" w jednym. Wystarczy posypać karmę — pełnia colostrum i kolagenu, a do tego smak, który zachęca do jedzenia.</p>
        </div>

        {/* benefit bullets */}
        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
          {bullets.map((b, i) => (
            <div key={i} style={{ display: 'flex', gap: 13, alignItems: 'flex-start', padding: '12px 0', borderBottom: i < 2 ? '1px solid var(--ga-gray-150)' : 'none' }}>
              <span style={{ flex: 'none', width: 28, height: 28, borderRadius: 999, background: '#FBF1DF', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <EIcon name="check" size={16} color="#C58A2E" />
              </span>
              <div>
                <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 15, margin: 0, color: 'var(--ga-ink)' }}>{b[0]}</p>
                <p style={{ fontSize: 13, color: 'var(--ga-gray-700)', margin: '2px 0 0', lineHeight: 1.5 }}>{b[1]}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 34 }}>
          <div style={{ textAlign: 'center' }}>
            <a className="em-btn em-btn--full" href="#" style={{ background: '#D69A3A', color: '#fff', boxShadow: '0 8px 20px rgba(214,154,58,.32)' }}>Wypróbuj Zooggies&nbsp;&nbsp;→</a>
            <p style={{ fontSize: 12, color: 'var(--ga-gray-500)', margin: '12px 0 0' }}>64,00 zł · darmowa dostawa od 99 zł</p>
          </div>
        </div>

        <EmailFooter />
      </div>
    </div>
  );
}
window.EmailZB = EmailZB;
