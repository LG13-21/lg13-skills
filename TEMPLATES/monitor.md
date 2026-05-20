---
name: {{name}}
description: {{description}}. Triggers: '{{trigger1}}', '{{trigger2}}'
status: experimental
user-invocable: true
---

# {{name}}

## PURPOSE

{{purpose}}

Persistent Monitor arm — nulový overhead, žádný polling. Monitor tool zachytí každý event.

---

## EXECUTION

### 1. Arm Monitor

Spusť Monitor tool s tímto příkazem:

```bash
python L:/LG13/app/agent/{{arm_script}}.py --instance {{instance}} --interval 2 --timeout 86400
```

Monitor tool zachytí každý `[{{NOTIFY_TAG}}]` řádek.

### 2. Na každý event

```bash
# Na [{{NOTIFY_TAG}}] event:
{{on_event_command}}
```

### 3. Zpracuj + pokračuj

```
[instance pracuje na tasku]
       ↓
[{{NOTIFY_TAG}} přijde]
       ↓
[přeruš, zpracuj event]
       ↓
[pokračuj v původním tasku]
```

---

## RULES

- Jedna instance, jeden arm — nespouštěj arm vícekrát
- Monitor přežije práci — nezastavuje se mezi eventy
- Interval 2s — rychlá reakce bez I/O floodování
- --timeout 86400 — arm žije 24h, watchdog restartuje

## RELATED

- Skill `tmonkey-listen` — referenční implementace Monitor arm
- Skill `ping-pong` — pingpong events přes filesystem
