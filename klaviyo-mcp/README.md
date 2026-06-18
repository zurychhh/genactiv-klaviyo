# klaviyo-segments MCP

Uzupelnia luke oficjalnego `klaviyo-mcp-server` (brak tworzenia/edycji segmentow).
Wystawia zapis na Segments API: `create_segment`, `create_rfm_segment`,
`update_segment`, `delete_segment` + odczyt `list_segments`, `get_segment`
(z `profile_count` = baseline liczebnosci).

## Auth
Klucz PRYWATNY Klaviyo (`pk_...`) ze scope `segments:write` w zmiennej
`KLAVIYO_API_KEY` (root `.env`). Generujesz: Klaviyo > Settings > API keys >
Create Private API Key > scope Segments: Full Access.

## Uruchomienie
    fastmcp run server.py
Lub przez `.mcp.json` (serwer `klaviyo-segments`) — patrz setup-claude.sh.

## RFM — metryka
Placed Order (Shopify) = `R6aTMS`. `measurement:"sum"` sumuje `$value` zamowien.
Logika: conditions w grupie = OR, osobne condition_groups = AND.
