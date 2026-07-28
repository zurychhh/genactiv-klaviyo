/* Genactiv ONBOARDING — shared building blocks (on top of parts.jsx).
   Depends on: EIcon, Preheader, EmailFooter (parts.jsx). */

function HeaderRed() {
  return (
    <div style={{ background: 'var(--ga-red)', padding: '22px 40px', textAlign: 'center' }}>
      <img src="../assets/logo-white.png" alt="Genactiv" style={{ height: 30, margin: '0 auto' }} />
    </div>
  );
}

function HeaderLight() {
  return (
    <div style={{ background: '#fff', padding: '24px 40px', textAlign: 'center', borderBottom: '1px solid var(--ga-gray-150)' }}>
      <img src="../assets/logo-primary.png" alt="Genactiv" style={{ height: 26, margin: '0 auto' }} />
    </div>
  );
}

function StepRail({ step, total = 5, center }) {
  const dots = [];
  for (let i = 1; i <= total; i++) {
    const cls = i === step ? 'onb-rail__dot onb-rail__dot--on' : (i < step ? 'onb-rail__dot onb-rail__dot--done' : 'onb-rail__dot');
    dots.push(<i key={i} className={cls} />);
  }
  const rail = (
    <div className="onb-rail">
      <span className="onb-rail__label">Krok {step} / {total}</span>
      <span className="onb-rail__dots">{dots}</span>
    </div>
  );
  return center ? <div style={{ display: 'flex', justifyContent: 'center' }}>{rail}</div> : rail;
}

function CodeBox({ code = 'START15', label = 'Twój kod na pierwszy zakup', sub = '−15% na cały koszyk · ważny 14 dni' }) {
  return (
    <div className="onb-code">
      <p className="onb-code__label">{label}</p>
      <div className="onb-code__value">{code}</div>
      <p className="onb-code__sub">{sub}</p>
    </div>
  );
}

function OrderStrip() {
  return (
    <div className="onb-order">
      <span className="onb-order__ic"><EIcon name="check" size={20} color="var(--ga-success)" stroke={2.6} /></span>
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, fontFamily: 'var(--ga-font-display)', fontWeight: 700, fontSize: 14, color: 'var(--ga-ink)' }}>Zamówienie przyjęte — jest już w drodze</p>
        <p style={{ margin: '2px 0 0', fontSize: 12, color: 'var(--ga-gray-500)' }}>Dostawa w 1–2 dni robocze</p>
        <div className="onb-order__logos">
          <img src="../assets/ship-dhl.svg" alt="DHL" />
          <img src="../assets/ship-inpost.svg" alt="InPost" />
        </div>
      </div>
    </div>
  );
}

function Ritual({ items }) {
  return (
    <div className="onb-ritual">
      {items.map((it, i) => (
        <div className="onb-ritual__row" key={i}>
          <div className="onb-ritual__num">{i + 1}</div>
          <div><p className="onb-ritual__t">{it.t}</p><p className="onb-ritual__d">{it.d}</p></div>
        </div>
      ))}
    </div>
  );
}

function Timeline({ items }) {
  return (
    <div className="onb-tl">
      {items.map((it, i) => (
        <div className="onb-tl__item" key={i}>
          <span className="onb-tl__dot">{i + 1}</span>
          <p className="onb-tl__when">{it.when}</p>
          <p className="onb-tl__t">{it.t}</p>
          <p className="onb-tl__d">{it.d}</p>
        </div>
      ))}
    </div>
  );
}

function ExpertQuote({ img = 'expert-monika.png', name = 'Monika Stromkie-Złomaniec', role = 'Dietetyk kliniczny', quote }) {
  return (
    <div className="onb-expert">
      <img src={'../assets/' + img} alt={name} />
      <div>
        <p className="onb-expert__q">„{quote}”</p>
        <p className="onb-expert__n">{name} · <span>{role}</span></p>
      </div>
    </div>
  );
}

function ExpertsRow() {
  const ex = [
    { img: 'expert-monika.png', n: 'M. Stromkie-Złomaniec', r: 'Dietetyk' },
    { img: 'expert-halasa.png', n: 'dr hab. n. med. Hałasa', r: 'Immunolog' },
    { img: 'expert-magda.png', n: 'Magda', r: 'Psychodietetyk' },
  ];
  return (
    <div className="onb-experts">
      {ex.map((e, i) => (
        <div className="onb-experts__c" key={i}>
          <img src={'../assets/' + e.img} alt={e.n} />
          <p className="onb-experts__n">{e.n}</p>
          <p className="onb-experts__r">{e.r}</p>
        </div>
      ))}
    </div>
  );
}

function ProductCard({ name, meta, reviews, price, old, img = 'photo-colostrum-nr1.png', bg = 'var(--ga-red)' }) {
  return (
    <div className="em-prod">
      <img className="em-prod__img" src={'../assets/' + img} alt="" style={{ background: bg }} />
      <div style={{ flex: 1 }}>
        <p className="em-prod__name">{name}</p>
        <p className="em-prod__meta">{meta}</p>
        {reviews != null && <div className="em-stars" style={{ margin: '7px 0 0' }}>★★★★★ <span style={{ color: 'var(--ga-gray-500)', fontSize: 12 }}>({reviews})</span></div>}
        <p className="em-prod__price">{old && <s>{old}</s>}{price}</p>
      </div>
    </div>
  );
}

function ReasonList({ items }) {
  return (
    <div className="onb-reasons">
      {items.map((it, i) => (
        <div className="onb-reason" key={i}>
          <span className="onb-reason__ic"><EIcon name={it.icon || 'check'} size={18} color="var(--ga-red)" /></span>
          <div><p className="onb-reason__t">{it.t}</p><p className="onb-reason__d">{it.d}</p></div>
        </div>
      ))}
    </div>
  );
}

function ReviewTile({ txt, who }) {
  return (
    <div className="onb-rev">
      <div className="onb-rev__stars">★★★★★</div>
      <p className="onb-rev__txt">„{txt}”</p>
      <p className="onb-rev__who">{who}</p>
    </div>
  );
}

function FamilyGrid({ items }) {
  return (
    <div className="onb-fam">
      {items.map((it, i) => (
        <div className="onb-fam__card" key={i}>
          <img className="onb-fam__img" src={'../assets/' + it.img} alt={it.name} style={it.bg ? { background: it.bg } : null} />
          <div className="onb-fam__body">
            <p className="onb-fam__name">{it.name}</p>
            <p className="onb-fam__desc">{it.desc}</p>
            <a className="onb-fam__lnk" href="#">{it.cta || 'Poznaj'} →</a>
          </div>
        </div>
      ))}
    </div>
  );
}

function TrustLine() {
  return (
    <div className="onb-trust">
      <div className="em-stars" style={{ fontSize: 16 }}>★★★★★</div>
      <p className="onb-trust__t">COLOSTRUM NR 1 W APTEKACH W POLSCE</p>
      <p className="onb-trust__s">na odporność* · zaufały nam tysiące rodzin</p>
    </div>
  );
}

function Badge1() {
  return <span className="onb-badge1"><EIcon name="check" size={14} color="var(--ga-red)" stroke={3} /> Colostrum nr 1 w aptekach</span>;
}

function UrgBar({ children }) {
  return <div className="onb-urg"><EIcon name="bell" size={15} color="var(--ga-gold)" />{children}</div>;
}

function BenefitsBlock({ title = 'Za co pokochasz nasze Colostrum' }) {
  return (
    <div style={{ background: 'var(--ga-gray-100)', padding: '28px 40px' }}>
      <p style={{ textAlign: 'center', fontFamily: 'var(--ga-font-display)', fontWeight: 800, fontSize: 15, margin: '0 0 20px', letterSpacing: '.02em' }}>{title}</p>
      <div className="em-benefits">
        <div className="em-benefit"><img src="../assets/icon-smak.png" alt="" /><span>SMAK</span></div>
        <div className="em-benefit"><img src="../assets/icon-naturalnosc.png" alt="" /><span>NATURALNOŚĆ</span></div>
        <div className="em-benefit"><img src="../assets/icon-forma.png" alt="" /><span>FORMY PODANIA</span></div>
      </div>
    </div>
  );
}

function ShipNudge() {
  return (
    <div className="em-ship">
      <EIcon name="truck" size={22} color="var(--ga-red)" />
      <span className="em-ship__txt">Darmowa dostawa od <strong>99&nbsp;zł</strong> — dorzuć drugi produkt do koszyka.</span>
    </div>
  );
}

Object.assign(window, {
  HeaderRed, HeaderLight, StepRail, CodeBox, OrderStrip, Ritual, Timeline,
  ExpertQuote, ExpertsRow, ProductCard, ReasonList, ReviewTile, FamilyGrid,
  TrustLine, Badge1, UrgBar, BenefitsBlock, ShipNudge,
});
