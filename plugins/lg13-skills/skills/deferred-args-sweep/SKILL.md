---
name: deferred-args-sweep
description: "Use when a ChatGPT thread (CGE export) may contain arguments that were deferred to another filing ('patří do F63', 'do doplnění odvolání', 'zatím nezapisovat') and you must verify they did not get lost — catalogs all CGE conversations per conv_id and lists each deferral as MIGRATED?/PENDING? against the latest filing version. Trigger: 'deferred args', 'odložené argumenty', 'co jsme odložili', 'sweep vlákna', 'cge katalog'."
user-invocable: true
---

# deferred-args-sweep

Skript: `L:/GitHub/lg13-coder/agent/skills/deferred_args_sweep.py` (čte jen, nic nezapisuje do podání ani do `case/state/ARGUMENT_INVENTORY.md`).

```bash
# katalog: conv_id -> titul, počet zpráv, poslední zpráva, F-odkazy, stav sweepu (-> L:/LG13/runtime/cge_catalog.json)
python L:/GitHub/lg13-coder/agent/skills/deferred_args_sweep.py catalog
# sweep jednoho vlákna
python L:/GitHub/lg13-coder/agent/skills/deferred_args_sweep.py sweep --conv-id <id> --since YYYY-MM-DD --out <out.md>
```

- Zdroj: `legal-ship-2026/ChatGPT_export/*.json`; re-exporty téže konverzace -> bere se nejdelší.
- Detekce: jen odpovědi ChatGPT; jeden zásah na překrývající se okno; i bez F-čísla (cíl "doplnění odvolání" -> hledá nejlepší shodu napříč F*/); ledger/MIG zmínky bez F se zahazují.
- MIGRATED?/PENDING?: podíl klíčových slov (kmeny 6 znaků) nalezených v `F<N>/*<aktualni_verze>*.md`; práh 0.6. Je to nápověda, ne verdikt.
- Po sweepu: přečíst kontext zásahů v exportu, do inventáře zapisuje legal. Nic se neodesílá (STOP ORDER #1452).
