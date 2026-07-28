/* Genactiv UI kit — content sections */

function Benefits() {
  const items = [
    { img: '../../assets/icon-smak.png', label: 'SMAK' },
    { img: '../../assets/icon-naturalnosc.png', label: 'NATURALNOŚĆ' },
    { img: '../../assets/icon-forma.png', label: 'FORMY PODANIA' },
  ];
  return (
    <section className="section">
      <div className="ga-container">
        <div className="section__head">
          <span className="eyebrow">Suplement diety</span>
          <h2>Za co pokochasz nasze Colostrum?</h2>
        </div>
        <div className="benefits">
          {items.map((b) => (
            <div className="benefit" key={b.label}>
              <img src={b.img} alt="" />
              <span>{b.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function BrandStatement() {
  return (
    <section className="section section--cream">
      <div className="ga-container">
        <div className="split">
          <div className="split__media"><img src="../../assets/photo-colostrum-nr1.png" alt="Genactiv Colostrum" /></div>
          <div className="split__body">
            <span className="tag"><Icon name="shield-check" size={16} /> Nr 1 w aptekach w Polsce*</span>
            <h2>Genactiv® Colostrum.</h2>
            <p>Czyste, nieprzetworzone, bez dodatków i w 100% wierne naturze. <strong>250 składników aktywnych</strong> zamkniętych w jednej substancji. Jedyne na rynku colostrum dostępne w tylu formach podania i smakach. Polecane przez mamy i lubiane przez dzieci.</p>
            <p style={{ fontWeight: 700, color: 'var(--ga-red)' }}>GENACTIV®. Twój plan na zdrowie.</p>
            <Button variant="primary">Kup teraz<Icon name="arrow-right" size={18} /></Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function ProductCard({ p }) {
  const { add } = useCart();
  return (
    <article className="pcard" onClick={() => add(p.id)}>
      <div className="pcard__media" style={{ background: p.bg }}>
        {p.flag && <span className="pcard__flag">{p.flag}</span>}
        <button className="pcard__wish" aria-label="Dodaj do ulubionych" onClick={(e) => e.stopPropagation()}><Icon name="heart" size={18} /></button>
        <img src={p.img} alt={p.title} />
      </div>
      <div className="pcard__body">
        <span className="pcard__eye">{p.line}</span>
        <h3 className="pcard__title">{p.title}</h3>
        <div className="pcard__rating"><Stars n={p.rating} /> ({p.reviews})</div>
        <div className="pcard__foot">
          <span className="pcard__price">{p.was && <s>{zl(p.was)}</s>}{zl(p.price)}</span>
          <button className="pcard__add" onClick={(e) => { e.stopPropagation(); add(p.id); }}>Do koszyka</button>
        </div>
      </div>
    </article>
  );
}

function ProductSection() {
  return (
    <section className="section" id="sklep">
      <div className="ga-container">
        <div className="section__head">
          <span className="eyebrow">Bestsellery</span>
          <h2>Pokochasz całą rodziną</h2>
          <p>Colostrum, błonnik i wsparcie dla Twoich pupili — wszystko oparte na sile natury.</p>
        </div>
        <div className="pgrid">
          {PRODUCTS.map((p) => <ProductCard key={p.id} p={p} />)}
        </div>
      </div>
    </section>
  );
}

function SubBrandBand({ kicker, title, body, cta, img, bg, ctaVariant = 'white' }) {
  return (
    <div className="band" style={{ background: bg }}>
      <div className="band__body">
        <span className="eyebrow">{kicker}</span>
        <h2>{title}</h2>
        <p>{body}</p>
        <Button variant={ctaVariant}>{cta}<Icon name="arrow-right" size={18} /></Button>
      </div>
      <div className="band__media"><img src={img} alt="" /></div>
    </div>
  );
}

function SubBrands() {
  return (
    <section className="section section--alt">
      <div className="ga-container" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
        <SubBrandBand bg="var(--ga-pink)" kicker="Powered by Genactiv® Colostrum"
          title="Poznaj Genactiv® Fiberbiom"
          body="Synergia dwóch składników aktywnych: rozpuszczalny błonnik z kory modrzewia i Genactiv® Colostrum. Wspiera mikrobiotę, barierę jelitową i komfort trawienny."
          cta="Odkryj" img="../../assets/photo-fiberbiom.jpg" />
        <SubBrandBand bg="#E9B872" kicker="Powered by Genactiv® Colostrum"
          title="ZOOGGIES — zdrowie Twojego pupila"
          body="Bogaty suplement pełen colostrum i kolagenu, a do tego świetny „dosmaczacz” do karmy. Masz niejadka? Po prostu posyp. I gotowe!"
          cta="Odkryj" img="../../assets/photo-zooggies.jpg" />
        <SubBrandBand bg="var(--ga-graphite)" kicker="Linia DERMO"
          title="Twój plan na zdrową skórę i włosy"
          body="Kosmetyki z colostrum bovinum i mlekiem klaczy — dla cery dojrzałej, problematycznej i podrażnionej. Synergia dwóch darów natury."
          cta="Dowiedz się więcej" img="../../assets/photo-dermo.webp" />
      </div>
    </section>
  );
}

function Experts() {
  const ex = [
    { img: '../../assets/expert-monika.png', name: 'Monika Stromkie-Złomaniec', role: 'Dietetyk' },
    { img: '../../assets/expert-halasa.png', name: 'dr hab. n. med. Maciej Hałasa', role: 'Specjalista immunolog' },
    { img: '../../assets/expert-magda.png', name: 'Magdalena Szymczak-Kępka', role: 'Psycholog diagnosta, trycholog' },
  ];
  return (
    <section className="section">
      <div className="ga-container">
        <div className="section__head">
          <span className="eyebrow">Zaufali nam</span>
          <h2>Nasi eksperci</h2>
        </div>
        <div className="experts">
          {ex.map((e) => (
            <div className="expert" key={e.name}>
              <img src={e.img} alt={e.name} />
              <h4>{e.name}</h4>
              <span className="role">{e.role}</span>
              <a>Dowiedz się więcej <Icon name="chevron-right" size={14} /></a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Newsletter() {
  const [sent, setSent] = useState(false);
  return (
    <section className="section" style={{ paddingTop: 0 }}>
      <div className="ga-container">
        <div className="news">
          <h2>Twój plan na zdrowie zaczyna się tutaj</h2>
          <p>Zapisz się do newslettera — nowości i promocje COLOSTRUM GENACTIV.</p>
          <form className="news__form" onSubmit={(e) => { e.preventDefault(); setSent(true); }}>
            {sent
              ? <div style={{ color: '#fff', fontWeight: 700, width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8 }}><Icon name="check" size={20} color="#fff" /> Dziękujemy! Sprawdź skrzynkę.</div>
              : <React.Fragment><input type="email" placeholder="twoj@email.pl" required /><Button variant="primary" type="submit">Zapisz</Button></React.Fragment>}
          </form>
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { Benefits, BrandStatement, ProductCard, ProductSection, SubBrands, Experts, Newsletter });
