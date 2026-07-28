/* Genactiv UI kit — Promo bar + sticky Header + mobile nav + search overlay */
const NAV = ['Colostrum', 'Fiberbiom', 'Zooggies', 'Dermo', 'Poradnik'];

function PromoBar() {
  return (
    <div className="promo">
      <span>🚚 Darmowa dostawa w ten weekend — z okazji Dnia Dziecka, do 01/06 włącznie!</span>
    </div>
  );
}

function SearchOverlay({ open, onClose }) {
  const ref = useRef(null);
  useEffect(() => { if (open && ref.current) ref.current.focus(); }, [open]);
  return (
    <div className={'search' + (open ? ' is-open' : '')} onClick={onClose}>
      <div className="search__box" onClick={(e) => e.stopPropagation()}>
        <Icon name="search" size={26} color="var(--ga-ink)" />
        <input ref={ref} placeholder="Czego szukasz?" />
        <button className="iconbtn" onClick={onClose} aria-label="Zamknij"><Icon name="x" size={24} /></button>
      </div>
      <div className="search__hint" onClick={(e) => e.stopPropagation()}>
        {['Colostrum', 'Fiberbiom', 'Colostrum Junior', 'na odporność', 'Zooggies'].map((t) =>
          <button key={t}>{t}</button>)}
      </div>
    </div>
  );
}

function Header({ onMenu }) {
  const { count, setOpen } = useCart();
  const [search, setSearch] = useState(false);
  return (
    <header className="hdr">
      <div className="ga-container hdr__row">
        <button className="iconbtn hamburger" onClick={onMenu} aria-label="Menu"><Icon name="menu" /></button>
        <a className="hdr__logo" href="#top"><img src="../../assets/logo-primary.png" alt="Genactiv" /></a>
        <nav className="nav">
          {NAV.map((n) => <a key={n}>{n}{(n === 'Colostrum' || n === 'Zooggies') && <Icon name="chevron-down" size={15} />}</a>)}
        </nav>
        <div className="hdr__actions">
          <button className="iconbtn" aria-label="Szukaj" onClick={() => setSearch(true)}><Icon name="search" size={21} /></button>
          <button className="iconbtn" aria-label="Konto"><Icon name="user" size={21} /></button>
          <button className="iconbtn" aria-label="Ulubione"><Icon name="heart" size={21} /></button>
          <button className="iconbtn" aria-label="Koszyk" onClick={() => setOpen(true)}>
            <Icon name="cart" size={21} />
            {count > 0 && <span className="cart-count">{count}</span>}
          </button>
        </div>
      </div>
      <SearchOverlay open={search} onClose={() => setSearch(false)} />
    </header>
  );
}

Object.assign(window, { PromoBar, Header, NAV });
