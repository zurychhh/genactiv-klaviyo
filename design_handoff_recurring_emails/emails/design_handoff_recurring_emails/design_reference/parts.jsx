/* Genactiv emails — shared parts: Icon subset, Preheader, Footer */
const { useState } = React;

const EM_ICONS = {
  truck: '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  bell: '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  'arrow-right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  instagram: '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37Z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
  facebook: '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
  youtube: '<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
  heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
};
function EIcon({ name, size = 20, color = 'currentColor', stroke = 2, fill = 'none', style }) {
  return React.createElement('svg', {
    width: size, height: size, viewBox: '0 0 24 24', fill, stroke: color,
    strokeWidth: stroke, strokeLinecap: 'round', strokeLinejoin: 'round',
    style: { display: 'block', ...style },
    dangerouslySetInnerHTML: { __html: EM_ICONS[name] || '' },
  });
}

function Preheader({ text }) {
  return <div className="em-pre"><b>Podgląd:</b> {text}</div>;
}

function EmailFooter({ light }) {
  return (
    <div className={'em-foot' + (light ? ' em-foot--light' : '')}>
      <img src={light ? 'assets/logo-primary.png' : 'assets/logo-white.png'} alt="Genactiv" />
      <div className="em-foot__social">
        <a aria-label="Facebook"><EIcon name="facebook" size={16} /></a>
        <a aria-label="Instagram"><EIcon name="instagram" size={16} /></a>
        <a aria-label="YouTube"><EIcon name="youtube" size={16} /></a>
      </div>
      <p>Otrzymujesz tę wiadomość, bo kupujesz Genactiv® Colostrum.</p>
      <p><a className="link">Zmień częstotliwość</a> &nbsp;·&nbsp; <a className="link">Wypisz się</a></p>
      <p className="em-foot__legal">Genactiv Sp. z o.o. · ul. Polna 13/3, 62-070 Dąbrówka · NIP 9721202218<br />© 2026 Genactiv. Twój plan na zdrowie.</p>
    </div>
  );
}

Object.assign(window, { EIcon, Preheader, EmailFooter });
