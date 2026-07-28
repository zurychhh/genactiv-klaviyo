/* Genactiv UI kit — Hero slideshow */
const SLIDES = [
  { kicker: 'Dzień Dziecka', title: ['Weekend z ', 'darmową dostawą'], italic: 1,
    body: 'Z okazji Dnia Dziecka — promocja ważna od 29 do 01/06 włącznie. Zadbaj o odporność całej rodziny.',
    cta: 'Kup teraz', img: '../../assets/photo-colostrum-nr1.png', bg: 'var(--ga-red)' },
  { kicker: 'Nowość · Fiberbiom', title: ['Lekkość błonnika. ', 'Moc colostrum.'], italic: 1,
    body: 'Fiberbiom to unikalne połączenie rozpuszczalnego błonnika z kory modrzewia i Genactiv® Colostrum.',
    cta: 'Poznaj Fiberbiom', img: '../../assets/photo-fiberbiom.jpg', bg: 'var(--ga-pink)' },
  { kicker: 'Nr 1 w aptekach', title: ['Twój plan ', 'na zdrowie.'], italic: 1,
    body: 'Czyste, nieprzetworzone, w 100% wierne naturze. 250 składników aktywnych w jednej substancji.',
    cta: 'Odkryj Colostrum', img: '../../assets/photo-colostrum-nr1.png', bg: 'var(--ga-red)' },
];

function Hero() {
  const [i, setI] = useState(0);
  const [playing, setPlaying] = useState(true);
  const timer = useRef(null);
  useEffect(() => {
    if (!playing) return;
    timer.current = setInterval(() => setI((v) => (v + 1) % SLIDES.length), 5000);
    return () => clearInterval(timer.current);
  }, [playing]);

  return (
    <section className="hero" id="top">
      <div className="hero__track" style={{ transform: `translateX(-${i * 100}%)` }}>
        {SLIDES.map((s, idx) => (
          <div className="slide" key={idx} style={{ background: s.bg }}>
            <div className="ga-container">
              <div className="slide__inner">
                <span className="slide__kicker">{s.kicker}</span>
                <h1>{s.title[0]}<em>{s.title[1]}</em></h1>
                <p>{s.body}</p>
                <Button variant="white" size="lg">{s.cta}<Icon name="arrow-right" size={18} /></Button>
              </div>
              <div className="slide__photo"><img src={s.img} alt="" /></div>
            </div>
          </div>
        ))}
      </div>
      <div className="hero__dots">
        {SLIDES.map((_, idx) => (
          <button key={idx} className={idx === i ? 'is-active' : ''} onClick={() => setI(idx)} aria-label={'Slajd ' + (idx + 1)} />
        ))}
        <button className="hero__play" onClick={() => setPlaying((p) => !p)} aria-label="Play/Pause">
          {playing ? <span style={{ fontSize: 11, letterSpacing: 1 }}>❚❚</span> : <Icon name="chevron-right" size={16} />}
        </button>
      </div>
    </section>
  );
}
window.Hero = Hero;
