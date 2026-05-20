# meta.json — Schema a příklady

Každá složka podání obsahuje `meta.json` jako jediný zdroj pravdy o stavu.

## Kompletní schema

```json
{
  "rizeni": {
    "sp_zn": "0 P 29/2026",
    "drive_sp_zn": "37 P a Nc 39/2019",
    "soud": "Okresní soud v Českých Budějovicích",
    "ds_prijemce": "ws6abvh",
    "soudce": "JUDr. Ondřej Veselý"
  },
  "typ_podani": "Doplnění návrhu č. 1",
  "navrhovatel": {
    "jmeno": "Ing. Tomáš Kopecký",
    "nar": "1985-01-30",
    "ds": "vprwiuq"
  },
  "zakonna_zastupkyne": {
    "jmeno": "Lucie Řehoutová, roz. Kissová",
    "nar": "1984-06-16",
    "ds": "66jy64e",
    "advokat": "Mgr. Ondřej Flaška"
  },
  "stav": "waiting_strat | waiting_legal | waiting_t002 | waiting_tom | time_capsule | sent | cancelled | DRAFT — STOP drží",
  "aktualni_verze": "F10.3_S+L+O+_ASAP",
  "finalni_verze": null,
  "final_F_tag": "F10.0",
  "asap": true,
  "time_capsule_minutes": 5,
  "capsule_start_ts": null,
  "send_error": null,
  "locks": {
    "strat_check": null,
    "legal_check": null,
    "t002_check": null,
    "tom_approve": null,
    "time_lock": null
  },
  "versions": [
    {
      "v": "8.0",
      "timestamp": "2026-04-16T10:51:00",
      "author": "legal",
      "notes": "Popis změn"
    }
  ],
  "related_ds_messages": [
    {
      "dm_id": "1680642296",
      "direction": "sent",
      "timestamp": "2026-04-15T18:50:13",
      "delivered": "2026-04-15T18:52:08",
      "status": 6,
      "subject": "Doplnění návrhu ...",
      "note": "CHYBNÉ PODÁNÍ — vzato zpět"
    }
  ],
  "prilohy": [
    {
      "c": 1,
      "nazev": "Komentovaný výběr klíčových listin ze spisu OSPOD",
      "soubor": "priloha1_komentar_OSPOD.pdf"
    }
  ]
}
```

## Lock entry schema

```json
{
  "status": "PASS | FAIL | PASS with condition",
  "by": "strat | legal | t002 | tom | proxy",
  "timestamp": "2026-04-16T12:50:06",
  "notes": "Volný text — co bylo zkontrolováno, co bylo nalezeno"
}
```

## Stav workflow

| stav | Popis |
|------|-------|
| `waiting_strat` | Čeká na STRAT lock |
| `waiting_legal` | Čeká na LEGAL lock |
| `waiting_t002` | Čeká na T002 lock |
| `waiting_tom` | Čeká na TOM approve |
| `time_capsule` | TOM schválil, capsule běží |
| `sent` | Odesláno ISDS |
| `cancelled` | Zrušeno |
| `DRAFT — STOP drží` | Zastaveno (legacy stav) |

## Příklad plně vyplněného locks objektu (PASS)

```json
"locks": {
  "strat_check": {
    "status": "PASS",
    "by": "strat",
    "timestamp": "2026-04-16T12:50:06",
    "notes": "PDF čisté, DM zpětvzetí 1680755033 v textu, přílohy 7/7 match."
  },
  "legal_check": {
    "status": "PASS with condition",
    "by": "legal",
    "timestamp": "2026-04-16T12:50:47",
    "notes": "§465a/c/j OK, §888/889 novela 2026 monitoring (YELLOW R5)."
  },
  "t002_check": {
    "status": "PASS",
    "by": "t002",
    "timestamp": "2026-04-16T12:50:47",
    "notes": "PDF 156,479B Arial 14 stran. Přílohy 7/7. Žádné interní markery."
  },
  "tom_approve": {
    "status": "PASS",
    "by": "tom",
    "timestamp": "2026-04-16T13:15:00",
    "notes": "Tom R7 spot-check OK. Schvaluje odeslání."
  },
  "time_lock": {
    "status": "PASS",
    "by": "capsule",
    "timestamp": "2026-04-16T13:20:00",
    "notes": "ASAP 5 min uplynulo. Ready pro lock send."
  }
}
```
