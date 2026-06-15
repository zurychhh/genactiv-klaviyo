/* Email B — "Włącz cykliczną dostawę" — convert to subscription, save 15% */
function EmailB() {
  return (
    <div className="em">
      <Preheader text="Nie rób przerwy w odporności — i oszczędzaj 15% z każdą dostawą" />

      {/* light header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 40px', borderBottom: '1px solid var(--ga-gray-150)' }}>
        <img src="assets/logo-primary.png" alt="Genactiv" style={{ height: 28 }} />
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, background: 'var(--ga-red-soft)', color: 'var(--ga-red)', fontWeight: 700, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', padding: '7px 13px', borderRadius: 999 }}>
          <EIcon name="refresh" size={14} color="var(--ga-red)" /> Dostawa co 30 dni
        </span>
      </div>

      {/* hero */}
      <div className="em-pad" style={{ paddingBottom: 24 }}>
        <p className="em-eyebrow">Twój zapas się kończy</p>
        <h1 className="em-h1">Zadbaj o&nbsp;ciągłość. <em>Zaoszczędź 15%.</em></h1>
        <p className="em-body">Regularność jest kluczowa dla odporności. Włącz <strong>cykliczną dostawę</strong> — Colostrum dotrze do Ciebie co miesiąc, zanim się skończy, a Ty zapłacisz mniej. Bez zobowiązań, wstrzymasz lub anulujesz kiedy chcesz.</p>
      </div>

      {/* compare options */}
      <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 8 }}>
        <div style={{ display: 'flex', gap: 14 }}>
          {/* one-time */}
          <div style={{ flex: 1, border: '1.5px solid var(--ga-gray-300)', borderRadius: 16, padding: '18px 16px' }}>
            <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--ga-gray-500)', margin: 0 }}>Jednorazowo</p>
            <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 26, margin: '8px 0 2px' }}>79,00 zł</p>
            <p style={{ fontSize: 12, color: 'var(--ga-gray-500)', margin: 0 }}>jedno opakowanie</p>
          </div>
          {/* subscription highlighted */}
          <div style={{ flex: 1, position: 'relative', borderRadius: 16, padding: '18px 16px', background: 'var(--ga-red)', color: '#fff', boxShadow: '0 12px 28px rgba(245,51,63,.28)' }}>
            <span style={{ position: 'absolute', top: -11, right: 14, background: 'var(--ga-ink)', color: '#fff', fontSize: 10, fontWeight: 800, letterSpacing: '.06em', padding: '5px 10px', borderRadius: 999 }}>–15%</span>
            <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', opacity: .9, margin: 0 }}>Z subskrypcją</p>
            <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 26, margin: '8px 0 2px' }}>67,15 zł</p>
            <p style={{ fontSize: 12, opacity: .9, margin: 0 }}>co 30 dni + darmowa dostawa</p>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <a className="em-btn em-btn--red em-btn--full" href="#">Włącz cykliczną dostawę&nbsp;&nbsp;→</a>
          <a href="#" style={{ display: 'inline-block', marginTop: 14, fontSize: 13, fontWeight: 600, color: 'var(--ga-gray-700)', textDecoration: 'underline', textUnderlineOffset: 3 }}>Wolę zamówić jednorazowo</a>
        </div>
      </div>

      {/* expert quote */}
      <div className="em-pad" style={{ paddingTop: 28 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', background: 'var(--ga-cream)', borderRadius: 18, padding: 20 }}>
          <img src="assets/expert-monika.png" alt="" style={{ width: 64, height: 64, borderRadius: 999, objectFit: 'cover', flex: 'none' }} />
          <div>
            <p style={{ fontSize: 14, lineHeight: 1.5, fontStyle: 'italic', color: 'var(--ga-graphite)', margin: 0 }}>„Najlepsze efekty colostrum daje wtedy, gdy stosujemy je regularnie, bez przerw.”</p>
            <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--ga-red)', margin: '8px 0 0' }}>Monika Stromkie-Złomaniec · Dietetyk</p>
          </div>
        </div>
      </div>

      <div style={{ height: 16 }} />
      <EmailFooter light />
    </div>
  );
}
window.EmailB = EmailB;
