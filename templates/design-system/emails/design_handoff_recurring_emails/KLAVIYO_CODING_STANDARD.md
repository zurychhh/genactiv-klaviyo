# Genactiv — Standard kodowania maili w Klaviyo

Obowiązujący standard techniczny dla wszystkich maili marki **Genactiv** budowanych w Klaviyo.
Celem jest spójny, „bulletproof" kod, który renderuje się identycznie w głównych klientach
pocztowych i jest zgodny z systemem designu marki (kolory, typografia, ikonografia).

> Jeśli zespół Genactiv ma własny, wewnętrzny dokument standardu — ten plik należy z nim
> uzgodnić; poniższe reguły są rekomendacją wyprowadzoną z design systemu marki.

---

## 1. Zasady ogólne
1. **Tabele, nie flby/grid.** Layout wyłącznie na `<table role="presentation">` z
   `cellpadding="0" cellspacing="0" border="0"`. Brak `display:flex/grid` w strukturze nośnej.
2. **CSS inline.** Wszystkie style krytyczne dla layoutu — inline na elementach. `<style>` w
   `<head>` tylko dla: media queries (responsywność), dark mode, web-font `@import`/`<link>`,
   stanów `:hover` (progresywne ulepszenie).
3. **Szerokość 600 px.** Główny kontener `width:600`, na mobile `width:100%`.
4. **Jednostki w px.** Bez `rem`/`em` w layoucie. `line-height` jako liczba lub px.
5. **Obrazy:** zawsze `display:block`, jawne `width`, `border="0"`, sensowny `alt`.
   Pełnej szerokości obrazy: `width="100%"`. Retina: plik 2×, atrybut `width` = połowa.
6. **Brak background-image jako jedynego nośnika treści** (Outlook nie wspiera bez VML).
   Tła kolorowe = `bgcolor` + inline `background-color`.
7. **Kodowanie:** UTF-8 (`<meta charset="utf-8">`) — polskie znaki ą/ć/ę/ł/ń/ó/ś/ż/ź.

## 2. Boilerplate (punkt startowy każdego maila)
```html
<!doctype html>
<html lang="pl" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <!--[if mso]><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]-->
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,700;0,800;1,700&display=swap" rel="stylesheet">
  <title>Genactiv</title>
  <style>
    /* reset */
    body,table,td,a{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }
    table,td{ mso-table-lspace:0pt; mso-table-rspace:0pt; }
    img{ -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; display:block; }
    body{ margin:0; padding:0; width:100%!important; background:#F4F1EE; }
    a{ color:#F5333F; }
    /* responsywność */
    @media only screen and (max-width:600px){
      .ga-container{ width:100%!important; }
      .ga-pad{ padding-left:24px!important; padding-right:24px!important; }
      .ga-h1{ font-size:28px!important; }
      .ga-stack{ display:block!important; width:100%!important; }
      .ga-stack-gap{ height:14px!important; }
    }
    /* dark mode — utrzymaj czytelność, nie odwracaj brandu */
    @media (prefers-color-scheme: dark){
      .ga-darkbg{ background:#1C1B1B!important; }
      .ga-darktext{ color:#F4F1EE!important; }
    }
  </style>
</head>
<body>
  <!-- preheader (ukryty podgląd) -->
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#F4F1EE;">
    {{ PREHEADER_TEXT }}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#F4F1EE">
    <tr><td align="center" style="padding:24px 12px;">
      <table role="presentation" class="ga-container" width="600" cellpadding="0" cellspacing="0" border="0"
             style="width:600px;max-width:600px;background:#FFFFFF;border-radius:18px;overflow:hidden;">
        <!-- ↓ moduły maila ↓ -->
      </table>
    </td></tr>
  </table>
</body>
</html>
```

## 3. Typografia
- **Stack:** `font-family:'Montserrat', Arial, Helvetica, sans-serif;` — zawsze z fallbackiem.
- **Skala (px / weight / line-height):**
  - Eyebrow: 12 / 700 / 1.2 · `letter-spacing:1.5px` (~.16em) · UPPERCASE · `#F5333F`
  - H1: 34 / 800 / 1.1 · `#1C1B1B` (mobile 28 — patrz `.ga-h1`)
  - H2/sekcja: 22–26 / 800 / 1.15
  - Body: 15 / 400–500 / 1.6 · `#5C5757`
  - Meta/legal: 11–12 / 400 / 1.5 · `#8B8585`
- Kursywa nagłówków (np. „*Colostrum?*") = `<i>` lub `font-style:italic` na `<span>` —
  Montserrat ma realny italic; fallback Arial italic ok.
- CTA label: 13 / 700 / UPPERCASE / `letter-spacing:1.2px`.

## 4. Przyciski (bulletproof, pill)
Czerwony CTA, działa też w Outlooku (VML):
```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"><tr><td>
  <!--[if mso]>
  <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{{ CTA_URL }}" style="height:52px;v-text-anchor:middle;width:300px;" arcsize="50%" stroke="f" fillcolor="#F5333F">
  <w:anchorlock/><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;letter-spacing:1px;">ZAMÓW PONOWNIE</center>
  </v:roundrect>
  <![endif]-->
  <!--[if !mso]><!-- -->
  <a href="{{ CTA_URL }}" style="background:#F5333F;color:#ffffff;text-decoration:none;display:inline-block;
     font-family:'Montserrat',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;
     padding:16px 34px;border-radius:999px;">ZAMÓW PONOWNIE&nbsp;&nbsp;&rarr;</a>
  <!--<![endif]-->
</td></tr></table>
```
Warianty koloru: primary `#F5333F`, pink (Fiberbiom) `#F5669C`, ghost = przezroczyste tło +
`border:2px solid #F5333F` + tekst `#F5333F`. Stopka „white" = tło `#FFFFFF` + tekst `#F5333F`.

## 5. Klaviyo — tagi i dane dynamiczne
- **Personalizacja z fallbackiem (obowiązkowo):**
  `{{ first_name|default:'Cześć' }}` — nigdy „Witaj ,".
- **Właściwości profilu/eventu:** `{{ person.PROPERTY|default:'' }}`, `{{ event.PROPERTY }}`.
- **Produkty / katalog:** użyj dynamicznych bloków produktowych Klaviyo lub feedu katalogu;
  do rekomendacji/replenishment — blok produktu z ostatniego zamówienia lub Catalog.
- **Replenishment / „kończy się":** trigger flow **Placed Order** + time delay, albo metryka
  **Expected Date of Next Order** (predykcja Klaviyo). Liczba dni/porcji: właściwość profilu
  lub stały tekst fallback, gdy brak danych.
- **Ceny/waluta:** formatuj jako `zł` po wartości, przecinek dziesiętny (np. `79,00 zł`).
- **Linki:** dodawaj UTM (np. `?utm_source=klaviyo&utm_medium=email&utm_campaign=recurring_a`).
- **Wypis/Manage:** wyłącznie tagi Klaviyo — `{% unsubscribe %}`, `{% manage_preferences %}`.
- **Bloki warunkowe:** `{% if person.is_subscriber %} … {% else %} … {% endif %}`.

## 6. Obrazy i hosting
- Hostuj w **Klaviyo Image Library** lub firmowym CDN → **absolutne `https://` URL-e**.
- Każdy `<img>`: `alt`, `width` (px), `style="display:block;border:0;"`.
- Logo i ikony benefitów: dostarcz w 2× (retina), `width` = wymiar wyświetlany.
- Zdjęcia produktów: JPG/PNG zoptymalizowane (< ~200 KB), 1:1 dla hero produktu.
- Nie polegaj na obrazie tła dla kluczowej treści (Outlook). Tekst = realny tekst, nie obraz.

## 7. Dostępność i dostarczalność
- `lang="pl"`, sensowne `alt`, kontrast tekstu min. 4.5:1 (np. `#5C5757` na białym ✔).
- Realny tekst zamiast obrazów z tekstem (lepsza dostarczalność i dark mode).
- Stosunek tekst/obraz zrównoważony; preheader wypełniony; jeden główny CTA „nad linią".
- Stopka: pełne dane spółki (Genactiv Sp. z o.o., NIP 9721202218, adres) + powód otrzymania maila.

## 8. Konwencje nazewnictwa
- Szablony/UC bloki: `genactiv_recurring_{reminder|subscription|editorial}`.
- Klasy CSS w `<head>`: prefiks `ga-` (`ga-container`, `ga-pad`, `ga-h1`, `ga-stack`).
- Kampanie/flow w UTM: `recurring_a` / `recurring_b` / `recurring_c`.

## 9. Checklist przed publikacją
- [ ] Render: Apple Mail, Gmail (web + iOS/Android), Outlook (Win VML), Yahoo, Klaviyo preview.
- [ ] Dark mode nie psuje logo/tekstu (logo białe na ciemnym, tekst czytelny).
- [ ] Mobile ≤ 375 px: brak poziomego scrolla, CTA klikalne (≥ 44 px wysokości).
- [ ] Merge tagi z danymi i bez danych (fallbacky działają).
- [ ] Preheader poprawny i nie duplikuje H1.
- [ ] Wszystkie linki z UTM; `{% unsubscribe %}` obecny i działa.
- [ ] Polskie znaki poprawne (UTF-8). Alt-texty po polsku.
- [ ] Waga maila < ~100 KB HTML (unikaj „Gmail clipping").
