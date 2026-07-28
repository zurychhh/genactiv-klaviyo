/* Genactiv cross-sell emails — 3 kierunki na płótnie */
function CrossSellApp() {
  return (
    <DesignCanvas>
      <DCSection id="crosssell" title="Cross-sell — zachęta do innych kategorii" subtitle="3 kierunki · 600px · z Colostrum do Fiberbiom / Zooggies / DERMO">
        <DCArtboard id="cs1" label="1 · Fiberbiom (synergia, róż)" width={600} height={1124}><EmailCS1 /></DCArtboard>
        <DCArtboard id="cs2" label="2 · Zooggies (dla pupila, złoto)" width={600} height={1368}><EmailCS2 /></DCArtboard>
        <DCArtboard id="cs3" label="3 · DERMO (kosmetyki, editorial)" width={600} height={1330}><EmailCS3 /></DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<CrossSellApp />);
