# TODO: Remarketing Audit - Następne kroki

**Data utworzenia:** 2025-01-23
**Status:** W trakcie

---

## WYKONANE ✅

1. ✅ Deep dive audyt remarketingu
2. ✅ Identyfikacja głównej przyczyny (Pandectes cookiesBlockedByDefault=7)
3. ✅ Raport zapisany: `reports/REMARKETING_AUDIT_2025-01-23.md`

---

## DO ZROBIENIA 📋

### KROK 1: Wygeneruj OAuth token dla Google Ads MCP

**WYMAGANA INTERAKCJA UŻYTKOWNIKA:**

```bash
cd /Users/user/projects/genactiv-klaviyo/google-ads-mcp
source venv/bin/activate
python generate_refresh_token.py
```

1. Otworzy się przeglądarka z logowaniem Google
2. Zaloguj się na konto powiązane z Google Ads (Genactiv 253-832-8866)
3. Zezwól na dostęp do Google Ads API
4. Token zapisze się automatycznie
5. **Zrestartuj Claude Code**

---

### KROK 2: Po restarcie - sprawdzić w Google Ads

Po wygenerowaniu tokena, poproś Claude o:

```
Sprawdź ustawienia auto-tagging w Google Ads używając MCP
```

Rzeczy do zweryfikowania:
- [ ] Auto-tagging włączony/wyłączony
- [ ] Konfiguracja conversion tracking
- [ ] Remarketing audiences status
- [ ] Enhanced Conversions setup

---

### KROK 3: Wdrożenie rekomendacji

Z raportu `reports/REMARKETING_AUDIT_2025-01-23.md`:

1. [ ] Optymalizacja UX consent bannera w Pandectes
2. [ ] Wdrożenie Enhanced Conversions
3. [ ] Weryfikacja auto-tagging (po kroku 2)
4. [ ] Customer Match upload jako backup
5. [ ] Rozważenie Server-Side GTM

---

## KONTEKST DLA NOWEJ SESJI

**Główny problem:** Remarketing nie buduje audience

**Root cause:** Pandectes Consent Mode:
- `cookiesBlockedByDefault: "7"` - blokuje targeting cookies domyślnie
- `adStorageCategory: 4` - Google Ads wymaga explicit consent
- Campaign Attribution Rate = 1% (3/250 zamówień)

**Pliki do przeczytania:**
- `reports/REMARKETING_AUDIT_2025-01-23.md` - pełny raport
- `CLAUDE.md` - kontekst projektu

---

**Po wykonaniu KROKU 1, wróć do Claude z poleceniem:**
> "Kontynuuj audyt remarketingu - sprawdź Google Ads przez MCP (token już wygenerowany)"
