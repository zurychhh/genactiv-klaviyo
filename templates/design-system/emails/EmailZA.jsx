/* Zooggies A/B — Wariant A: EMOCJONALNY ("dla pupila"), złoto + zdjęcie hero */
function EmailZA() {
  return (
    <div>
      <ABMeta variant="A" subject="Ta sama natura — teraz dla Twojego pupila 🐾"
        preheader="Pokochali to ludzie. Pokocha i Twój pupil." />
      <div className="em">
        {/* light header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px 40px', borderBottom: '1px solid var(--ga-gray-150)' }}>
          <img src="../assets/logo-primary.png" alt="Genactiv" style={{ height: 28 }} />
        </div>

        <img src="../assets/photo-zooggies.jpg" alt="Zooggies" style={{ width: '100%', aspectRatio: '16 / 11', objectFit: 'cover' }} />

        <div className="em-pad" style={{ paddingBottom: 22 }}>
          <p className="em-eyebrow" style={{ color: '#C58A2E' }}>Powered by Genactiv® Colostrum</p>
          <h1 className="em-h1">Pokochali to ludzie. <em>Pokocha i Twój pupil.</em></h1>
          <p className="em-body">Z miłości do zwierząt i z tej samej nauki, której zaufały tysiące rodzin, narodziła się marka <strong>Zooggies</strong>. Colostrum i kolagen w jednym — a do tego świetny „dosmaczacz" do karmy.</p>
          <p className="em-body" style={{ marginTop: 10 }}>Masz niejadka? <strong>Po prostu posyp. I gotowe!</strong></p>
        </div>

        <div className="em-pad" style={{ paddingTop: 0, paddingBottom: 24 }}>
          <div className="em-prod" style={{ background: '#FBF1DF' }}>
            <img className="em-prod__img" src="../assets/photo-zooggies.jpg" alt="" style={{ background: '#E9B872' }} />
            <div style={{ flex: 1 }}>
              <p className="em-prod__name">Zooggies dla psów</p>
              <p className="em-prod__meta">Colostrum + kolagen · dosmaczacz</p>
              <div className="em-stars" style={{ margin: '7px 0 0' }}>★★★★★ <span style={{ color: 'var(--ga-gray-500)', fontSize: 12 }}>(51 opiekunów)</span></div>
              <p className="em-prod__price">64,00 zł</p>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: 22 }}>
            <a className="em-btn em-btn--full" href="#" style={{ background: '#D69A3A', color: '#fff', boxShadow: '0 8px 20px rgba(214,154,58,.32)' }}>Odkryj Zooggies&nbsp;&nbsp;→</a>
          </div>
        </div>

        <div style={{ background: '#FBF1DF', padding: '24px 40px', textAlign: 'center' }}>
          <p style={{ fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 14, color: 'var(--ga-graphite)', margin: 0, lineHeight: 1.5 }}>
            🐾 &nbsp;Bo zdrowie Twojego pupila zaczyna się tak samo — od natury.
          </p>
        </div>

        <EmailFooter />
      </div>
    </div>
  );
}
window.EmailZA = EmailZA;
