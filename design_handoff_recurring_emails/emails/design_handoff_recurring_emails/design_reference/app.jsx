/* Genactiv recurring-purchase emails — 3 directions on a design canvas */
function App() {
  return (
    <DesignCanvas>
      <DCSection id="recurring" title="Recurring purchase — przypomnienie o ponownym zakupie" subtitle="3 kierunki · 600px · Genactiv® Colostrum">
        <DCArtboard id="a" label="A · Przypomnienie (czerwony, pilny)" width={600} height={1160}><EmailA /></DCArtboard>
        <DCArtboard id="b" label="B · Subskrypcja –15% (konwersja)" width={600} height={1040}><EmailB /></DCArtboard>
        <DCArtboard id="c" label="C · Editorial (kremowy, premium)" width={600} height={1336}><EmailC /></DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
