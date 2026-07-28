/* Zooggies A/B test — 3 warianty na płótnie */
function ZooggiesABApp() {
  return (
    <DesignCanvas>
      <DCSection id="zooggies-ab" title="Zooggies — test A/B (3 warianty)" subtitle="Stała oferta i stopka · zmienny kąt: emocje / problem / autorytet">
        <DCArtboard id="za" label="A · Emocjonalny (dla pupila)" width={600} height={1416}><EmailZA /></DCArtboard>
        <DCArtboard id="zb" label="B · Problem → rozwiązanie (niejadek)" width={600} height={1246}><EmailZB /></DCArtboard>
        <DCArtboard id="zc" label="C · Autorytet + dowód społeczny" width={600} height={1156}><EmailZC /></DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<ZooggiesABApp />);
