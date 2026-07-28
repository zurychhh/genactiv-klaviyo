/* Genactiv — Onboarding email sequences (2 ścieżki × 5 kroków × 2 warianty).
   Wariant A = śmiały/czerwony · Wariant B = editorial/kremowy. 600px. */
function App() {
  return (
    <DesignCanvas>
      {/* ── ŚCIEŻKA 1: PO 1. ZAKUPIE ── */}
      <DCSection id="pur1" title="PO ZAKUPIE · Krok 1 — Powitanie i potwierdzenie" subtitle="Trigger: Placed Order · 2 warianty · 600px">
        <DCArtboard id="p1a" label="A · Śmiały (czerwony)" width={600} height={1024}><PurStep1A /></DCArtboard>
        <DCArtboard id="p1b" label="B · Editorial (kremowy)" width={600} height={1320}><PurStep1B /></DCArtboard>
      </DCSection>

      <DCSection id="pur2" title="PO ZAKUPIE · Krok 2 — Jak stosować" subtitle="Delay ~2 dni · dawkowanie, rytuał">
        <DCArtboard id="p2a" label="A · Śmiały (czerwony)" width={600} height={1224}><PurStep2A /></DCArtboard>
        <DCArtboard id="p2b" label="B · Editorial (kremowy)" width={600} height={1180}><PurStep2B /></DCArtboard>
      </DCSection>

      <DCSection id="pur3" title="PO ZAKUPIE · Krok 3 — Czego się spodziewać" subtitle="Delay ~7 dni · timeline efektów">
        <DCArtboard id="p3a" label="A · Śmiały (czerwony)" width={600} height={1180}><PurStep3A /></DCArtboard>
        <DCArtboard id="p3b" label="B · Editorial (kremowy)" width={600} height={1180}><PurStep3B /></DCArtboard>
      </DCSection>

      <DCSection id="pur4" title="PO ZAKUPIE · Krok 4 — Cross-sell: Fiberbiom" subtitle="Delay ~14 dni · synergia, akcent różowy">
        <DCArtboard id="p4a" label="A · Śmiały (różowy CTA)" width={600} height={1020}><PurStep4A /></DCArtboard>
        <DCArtboard id="p4b" label="B · Editorial (kremowy)" width={600} height={1200}><PurStep4B /></DCArtboard>
      </DCSection>

      <DCSection id="pur5" title="PO ZAKUPIE · Krok 5 — Cała rodzina + opinia" subtitle="Delay ~21 dni · cross-sell + review request">
        <DCArtboard id="p5a" label="A · Śmiały (czerwony)" width={600} height={1180}><PurStep5A /></DCArtboard>
        <DCArtboard id="p5b" label="B · Editorial (kremowy)" width={600} height={1080}><PurStep5B /></DCArtboard>
      </DCSection>

      {/* ── ŚCIEŻKA 2: BEZ ZAKUPU (lead nurture) ── */}
      <DCSection id="nur1" title="BEZ ZAKUPU · Krok 1 — Powitanie + kod −15%" subtitle="Trigger: Newsletter signup · 2 warianty · 600px">
        <DCArtboard id="n1a" label="A · Śmiały (czerwony)" width={600} height={1320}><NurStep1A /></DCArtboard>
        <DCArtboard id="n1b" label="B · Editorial (kremowy)" width={600} height={1240}><NurStep1B /></DCArtboard>
      </DCSection>

      <DCSection id="nur2" title="BEZ ZAKUPU · Krok 2 — Dlaczego colostrum" subtitle="Delay ~2 dni · edukacja, problem → rozwiązanie">
        <DCArtboard id="n2a" label="A · Śmiały (czerwony)" width={600} height={1200}><NurStep2A /></DCArtboard>
        <DCArtboard id="n2b" label="B · Editorial (kremowy)" width={600} height={1160}><NurStep2B /></DCArtboard>
      </DCSection>

      <DCSection id="nur3" title="BEZ ZAKUPU · Krok 3 — Dowód społeczny" subtitle="Delay ~4 dni · nr 1, opinie, eksperci">
        <DCArtboard id="n3a" label="A · Śmiały (czerwony)" width={600} height={1180}><NurStep3A /></DCArtboard>
        <DCArtboard id="n3b" label="B · Editorial (kremowy)" width={600} height={1100}><NurStep3B /></DCArtboard>
      </DCSection>

      <DCSection id="nur4" title="BEZ ZAKUPU · Krok 4 — Przypomnienie o kodzie" subtitle="Delay ~6 dni · urgency 48h">
        <DCArtboard id="n4a" label="A · Śmiały (czerwony)" width={600} height={1140}><NurStep4A /></DCArtboard>
        <DCArtboard id="n4b" label="B · Editorial (kremowy)" width={600} height={1160}><NurStep4B /></DCArtboard>
      </DCSection>

      <DCSection id="nur5" title="BEZ ZAKUPU · Krok 5 — Ostatnie wołanie" subtitle="Delay ~8 dni · last call, kod znika dziś">
        <DCArtboard id="n5a" label="A · Śmiały (czerwony)" width={600} height={1160}><NurStep5A /></DCArtboard>
        <DCArtboard id="n5b" label="B · Editorial (kremowy)" width={600} height={1240}><NurStep5B /></DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
