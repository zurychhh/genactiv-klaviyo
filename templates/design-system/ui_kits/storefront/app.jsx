/* Genactiv UI kit — App composition */
function MobileNav({ open, onClose }) {
  const { setOpen } = useCart();
  return (
    <React.Fragment>
      <div className={'scrim' + (open ? ' is-open' : '')} onClick={onClose} style={{ zIndex: 95 }} />
      <aside className={'drawer' + (open ? ' is-open' : '')} style={{ left: 0, right: 'auto', transform: open ? 'translateX(0)' : 'translateX(-100%)', width: 320 }}>
        <div className="drawer__head">
          <img src="../../assets/logo-primary.png" alt="Genactiv" style={{ height: 30 }} />
          <button className="iconbtn" onClick={onClose} aria-label="Zamknij"><Icon name="x" size={22} /></button>
        </div>
        <nav style={{ padding: '8px 12px', display: 'flex', flexDirection: 'column' }}>
          {NAV.map((n) => (
            <a key={n} onClick={onClose} style={{ padding: '15px 12px', fontFamily: 'var(--ga-font-display)', fontWeight: 600, fontSize: 17, color: 'var(--ga-ink)', textDecoration: 'none', borderBottom: '1px solid var(--ga-gray-150)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
              {n}<Icon name="chevron-right" size={18} color="var(--ga-gray-500)" />
            </a>
          ))}
        </nav>
      </aside>
    </React.Fragment>
  );
}

function App() {
  const [menu, setMenu] = useState(false);
  return (
    <CartProvider>
      <PromoBar />
      <Header onMenu={() => setMenu(true)} />
      <MobileNav open={menu} onClose={() => setMenu(false)} />
      <main>
        <Hero />
        <Benefits />
        <BrandStatement />
        <ProductSection />
        <SubBrands />
        <Experts />
        <Newsletter />
      </main>
      <Footer />
      <CartDrawer />
      <Toast />
    </CartProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
