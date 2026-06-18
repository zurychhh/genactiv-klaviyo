# Notatka: Claude Design, Cowork i narzędzia AI do generowania

*Spisane: czerwiec 2026. Branża AI-gen zmienia się szybko — traktuj nazwy modeli jako stan na połowę 2026.*

---

## 1. Claude Design vs Cowork vs Claude Code — co jest czym

| Produkt | Do czego | Gdzie działa |
|---|---|---|
| **Claude Design** (Anthropic Labs) | Praca **wizualna**: projekty UI, prototypy, slajdy, one-pagery, makiety, marketing collateral. Czyta kod/pliki → buduje **design system** i reużywa go | Claude.ai / Labs (research preview), silnik Opus 4.7 |
| **Claude Code** (CLI/IDE) | Zamiana projektu w **produkcyjny kod**. Cel „handoffu" z Design; wpina Figmę | terminal / IDE / desktop |
| **Cowork** | Agentowa praca **niekodowa**: raporty, synteza dokumentów, dane. „Moc Claude Code dla pracy biurowej" | Claude Desktop |

**Kluczowe:** Cowork NIE jest do projektowania. Design ≠ Claude Code — w Claude Code się *wdraża*, nie projektuje.

---

## 2. Claude Design — jak korzystać i zależność od planu

**Co stworzysz:** prototypy interaktywne, wireframe'y, eksploracja wielu kierunków, landing/social/kampanie, decki, prototypy „code-powered" (3D/shadery/wideo).
**Import:** tekst, obrazy, DOCX/PPTX/XLSX, istniejące strony WWW.
**Export:** Canva, PDF, PPTX, HTML, wewnętrzny URL.
**Handoff:** pakuje projekt w *bundle* → przekazujesz do Claude Code jedną komendą.

**Jak dobrze:** 1) najpierw skonfiguruj design system (czyta codebase/brand), 2) dawaj kontekst na wejściu (strony/screeny), 3) proś o kilka kierunków, 4) dopieszczaj inline (komentarze, edycja tekstu, pokrętła), 5) handoff do kodu.

**Plany:**
| Plan | Dostęp | Uwaga |
|---|---|---|
| Pro / Max | ✅ od ręki | standardowe limity planu (Max = więcej) |
| Team | ✅ | admin włącza: Ustawienia org → Capabilities → Anthropic Labs |
| Enterprise | ✅, domyślnie **OFF** | admin musi włączyć; sterowanie przez custom roles |

Limity: brak sztywnych, brak ograniczeń seatów — korzysta ze standardowych limitów subskrypcji + opcjonalne płatne overage. „Pole do popisu" = ile daje Twój plan.

Źródła: anthropic.com/news/claude-design-anthropic-labs · support.claude.com (admin guide + design system setup).

---

## 3. Budowa efektownych stron (Shopify Editions / Higgsfield jako referencje)

- **Layout, sekcje, siatki, typografia, modale** → ✅ spokojnie (Design → kod).
- **Motion** (scroll, parallax, reveal, micro-interakcje) → ✅ realne, praca iteracyjna (GSAP/CSS).
- **3D / WebGL / shadery** → ⚠️ osiągalne, ale najdroższa część (Three.js/WebGL), wiele rund.
- **Styl „dark cinematic" (jak Higgsfield)** → łatwiejszy niż 3D-spektakl, bo „wow" napędza **jakość wideo**, nie egzotyczny kod.

**Wniosek:** wąskim gardłem nie jest kod (to robię tutaj), tylko **materiały wideo/foto**. Replikacja 1:1 topowej strony = projekt na kilka–kilkanaście iteracji.

---

## 4. Narzędzia AI do generowania — mapa

| Kategoria | Topowe | Wybór |
|---|---|---|
| **Wideo** | Veo 3, Sora 2, Kling, Runway, Higgsfield | jakość → Veo 3/Sora 2 · kontrola+montaż → Runway · dużo stylów → Higgsfield |
| **Obrazy** | Midjourney, Flux, Nano Banana Pro, Recraft, Ideogram, Firefly | estetyka → Midjourney · edycja/spójność → Nano Banana · brand/tekst → Recraft/Ideogram |
| **All-in-one** | Krea, Higgsfield, Freepik AI, Leonardo | jeden abonament na wszystko → Krea |
| **Audio** | Suno (muzyka), ElevenLabs (lektor/SFX) | — |
| **3D** | Meshy, Luma | — |

**3 pytania, które przecinają wybór:** wideo czy obrazy? komercyjnie? kontrola czy szybkość?

---

## 5. Moja rekomendacja (dla: oba, eksperymenty teraz, może komercyjnie później)

**Start: Krea** (lub Higgsfield przy nacisku na wideo).
- jeden abonament, obraz + wideo, model miesięczny — eksperymentujesz bez zobowiązań,
- agreguje topowe modele, poznasz style zanim zainwestujesz na poważnie.

**Zasady na „potem komercyjnie":**
1. Nie buduj produkcyjnego pipeline'u, dopóki nie wiesz, że materiał leci na sprzedaż.
2. Trzymaj prompty/workflow przenośne (zapisuj co i jak generujesz).
3. Gdy coś realnie idzie komercyjnie → ten konkretny asset przegeneruj/zweryfikuj prawa w narzędziu z czystą licencją: **Firefly** (obrazy) lub **Runway/Veo** (wideo).
4. Unikaj opierania kampanii „w ciemno" na Midjourney/Sora bez sprawdzenia licencji.

**Best-of-breed (gdy zależy na maks. jakości):** Midjourney (obrazy) + Runway/Veo (wideo) — wyższy sufit, ale 2 subskrypcje.

---

## 6. Integracja z Claude Code — stan konektorów

- **Brak MCP/konektora** do Higgsfield/Runway/Sora/Krea w obecnej konfiguracji.
- Workflow: generujesz asset w narzędziu → wrzucasz plik → Claude Code wpina go w stronę/projekt (ręcznie, ale działa).
- Podpięte i pomocne przy materiałach: **Canva**, **Figma** (+ upload obrazów do Klaviyo).

---

## Następne możliwe kroki
- Próbny hero/sekcja w kodzie (żeby zobaczyć poziom bez dodatkowych narzędzi).
- Ułożenie przenośnego workflow do nazewnictwa/zapisu promptów i assetów.
- Konfiguracja design systemu w Claude Design (gdy plan to umożliwia).
