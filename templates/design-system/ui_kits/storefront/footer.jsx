/* Genactiv UI kit — Footer */
function Footer() {
  const cols = [
    { h: 'Genactiv', links: ['O Nas', 'Poradnik', 'FAQ', 'Klub Hodowcy', 'Polityka Jakości ISO'] },
    { h: 'Obsługa klienta', links: ['Kontakt', 'Formy płatności', 'Formy dostawy', 'Zwroty', 'Regulamin'] },
    { h: 'Produkty', links: ['Colostrum', 'Fiberbiom', 'Zooggies', 'Dermo', 'Colostrum Junior'] },
  ];
  const pays = [
    { src: '../../assets/pay-przelewy24.svg', alt: 'Przelewy24' },
    { src: '../../assets/pay-blik.svg', alt: 'BLIK' },
    { src: '../../assets/pay-pobranie.svg', alt: 'Za pobraniem' },
    { src: '../../assets/ship-dhl.svg', alt: 'DHL' },
    { src: '../../assets/ship-inpost.svg', alt: 'InPost' },
  ];
  return (
    <footer className="footer">
      <div className="ga-container">
        <div className="footer__top">
          <div className="footer__brand">
            <img src="../../assets/logo-primary.png" alt="Genactiv" />
            <p>Genactiv Sp. z o.o. — producent suplementów z colostrum i mlekiem klaczy. Twój plan na zdrowie.</p>
            <div className="footer__social">
              <a aria-label="Facebook"><Icon name="facebook" size={18} /></a>
              <a aria-label="Instagram"><Icon name="instagram" size={18} /></a>
              <a aria-label="YouTube"><Icon name="youtube" size={18} /></a>
            </div>
          </div>
          {cols.map((c) => (
            <div className="footer__col" key={c.h}>
              <h5>{c.h}</h5>
              {c.links.map((l) => <a key={l}>{l}</a>)}
            </div>
          ))}
        </div>
        <div className="footer__bottom">
          <span className="footer__legal">© 2026 Genactiv Sp. z o.o. · NIP 9721202218 · Poznań, Polska</span>
          <div className="footer__pay">
            {pays.map((p) => <img key={p.alt} src={p.src} alt={p.alt} title={p.alt} />)}
          </div>
        </div>
      </div>
    </footer>
  );
}
window.Footer = Footer;
