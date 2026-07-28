/* Genactiv UI kit — Cart drawer + toast */
const FREE_SHIP = 99;

function CartDrawer() {
  const { items, open, setOpen, setQty, remove, subtotal } = useCart();
  const remaining = Math.max(0, FREE_SHIP - subtotal);
  const pct = Math.min(100, (subtotal / FREE_SHIP) * 100);
  return (
    <React.Fragment>
      <div className={'scrim' + (open ? ' is-open' : '')} onClick={() => setOpen(false)} />
      <aside className={'drawer' + (open ? ' is-open' : '')} aria-hidden={!open}>
        <div className="drawer__head">
          <h3>Twój koszyk</h3>
          <button className="iconbtn" onClick={() => setOpen(false)} aria-label="Zamknij"><Icon name="x" size={22} /></button>
        </div>

        {items.length === 0 ? (
          <div className="drawer__empty">
            <Icon name="cart" size={42} color="var(--ga-gray-300)" />
            <p>Twój koszyk jest obecnie pusty.</p>
            <Button variant="ghost" onClick={() => setOpen(false)}>Kontynuuj zakupy</Button>
          </div>
        ) : (
          <React.Fragment>
            <div className="ship-bar">
              <div className="ship-bar__cap">
                <Icon name="truck" size={17} color="var(--ga-red)" />
                {remaining > 0
                  ? <span>Jeszcze <strong>{zl(remaining)}</strong> do darmowej dostawy</span>
                  : <span><strong>Gratulacje — masz darmową dostawę!</strong></span>}
              </div>
              <div className="ship-bar__track"><i style={{ width: pct + '%' }} /></div>
            </div>

            <div className="drawer__items">
              {items.map((it) => {
                const p = PRODUCTS.find((p) => p.id === it.id);
                return (
                  <div className="citem" key={it.id}>
                    <img src={p.img} alt={p.title} style={{ background: p.bg }} />
                    <div className="citem__main">
                      <div className="citem__title">{p.title}</div>
                      <div className="citem__row">
                        <div className="qty">
                          <button onClick={() => setQty(it.id, it.qty - 1)} aria-label="Mniej"><Icon name="minus" size={14} /></button>
                          <span>{it.qty}</span>
                          <button onClick={() => setQty(it.id, it.qty + 1)} aria-label="Więcej"><Icon name="plus" size={14} /></button>
                        </div>
                        <span className="citem__price">{zl(p.price * it.qty)}</span>
                      </div>
                      <button className="citem__remove" onClick={() => remove(it.id)}>Usuń</button>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="drawer__foot">
              <div className="drawer__subtotal">
                <span className="lbl">Razem <span style={{ color: 'var(--ga-gray-500)', fontSize: 12 }}>(z VAT)</span></span>
                <span className="val">{zl(subtotal)}</span>
              </div>
              <Button variant="primary" className="btn--full btn--lg">Przejdź do kasy</Button>
            </div>
          </React.Fragment>
        )}
      </aside>
    </React.Fragment>
  );
}

function Toast() {
  const { toast } = useCart();
  return (
    <div className={'toast' + (toast ? ' is-open' : '')}>
      <Icon name="check" size={18} color="var(--ga-success)" />{toast}
    </div>
  );
}

Object.assign(window, { CartDrawer, Toast });
