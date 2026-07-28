/* Genactiv UI kit — shared atoms, data, helpers */
const { useState, useEffect, useRef, createContext, useContext } = React;

const zl = (n) => n.toFixed(2).replace('.', ',') + ' zł';

const PRODUCTS = [
  { id: 'col-kaps', title: 'Colostrum Genactiv, kapsułki', line: 'Suplement diety · 60 kapsułek',
    price: 69, rating: 5, reviews: 412, flag: 'NR 1 W APTEKACH', img: '../../assets/photo-colostrum-nr1.png', bg: 'var(--ga-red)' },
  { id: 'col-proszek', title: 'Colostrum Genactiv, proszek', line: 'Suplement diety · 45 g',
    price: 79, rating: 5, reviews: 214, img: '../../assets/photo-colostrum-nr1.png', bg: 'var(--ga-red)' },
  { id: 'fiberbiom', title: 'Fiberbiom', line: 'Błonnik + Colostrum · 15 saszetek',
    price: 89, was: 99, rating: 5, reviews: 88, flag: 'NOWOŚĆ', img: '../../assets/photo-fiberbiom.jpg', bg: 'var(--ga-pink)' },
  { id: 'zooggies', title: 'Zooggies dla psów', line: 'Suplement · colostrum + kolagen',
    price: 64, rating: 5, reviews: 51, img: '../../assets/photo-zooggies.jpg', bg: '#E9B872' },
];

function Stars({ n = 5 }) {
  return (
    <span className="stars" aria-label={n + ' / 5'}>
      {Array.from({ length: 5 }).map((_, i) =>
        <Icon key={i} name="star" size={13} fill={i < n ? 'var(--ga-gold)' : 'none'} color="var(--ga-gold)" stroke={1.5} />)}
    </span>
  );
}

function Button({ variant = 'primary', size, children, className = '', ...rest }) {
  const cls = ['btn', 'btn--' + variant, size ? 'btn--' + size : '', className].filter(Boolean).join(' ');
  return <button className={cls} {...rest}>{children}</button>;
}

/* ---- Cart store (simple context) ---- */
const CartCtx = createContext(null);
const useCart = () => useContext(CartCtx);

function CartProvider({ children }) {
  const [items, setItems] = useState([]);      // {id, qty}
  const [open, setOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);

  const add = (id) => {
    setItems((cur) => {
      const found = cur.find((i) => i.id === id);
      if (found) return cur.map((i) => i.id === id ? { ...i, qty: i.qty + 1 } : i);
      return [...cur, { id, qty: 1 }];
    });
    const p = PRODUCTS.find((p) => p.id === id);
    setToast('Dodano: ' + p.title);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2200);
    setOpen(true);
  };
  const setQty = (id, q) => setItems((cur) => q <= 0 ? cur.filter((i) => i.id !== id) : cur.map((i) => i.id === id ? { ...i, qty: q } : i));
  const remove = (id) => setItems((cur) => cur.filter((i) => i.id !== id));
  const count = items.reduce((s, i) => s + i.qty, 0);
  const subtotal = items.reduce((s, i) => s + i.qty * PRODUCTS.find((p) => p.id === i.id).price, 0);

  return (
    <CartCtx.Provider value={{ items, open, setOpen, add, setQty, remove, count, subtotal, toast }}>
      {children}
    </CartCtx.Provider>
  );
}

Object.assign(window, { zl, PRODUCTS, Stars, Button, CartProvider, useCart });
