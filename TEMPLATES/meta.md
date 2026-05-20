---
name: {{name}}
description: {{description}}. Triggers: '{{trigger1}}', '{{trigger2}}'
status: experimental
user-invocable: true
---

# {{name}}

## PURPOSE

{{purpose}}

Meta-skill — operuje na jiných skills nebo na skill systému samotném.

---

## EXECUTION

### 1. Read current state

```bash
# Přečti stav toho, co chceš ovlivnit
{{read_command}}
```

### 2. Validate

```
Zkontroluj prerekvizity:
- {{prereq1}}
- {{prereq2}}
Pokud chybí → fail fast + ukaž co chybí
```

### 3. Execute change

```bash
{{execute_command}}
```

### 4. Verify + report

```bash
{{verify_command}}
```

---

## OUTPUT

- Stav PŘED: `{{before_state}}`
- Stav PO: `{{after_state}}`
- Co se změnilo: `{{delta}}`

---

## RULES

- Vždy validuj PŘED změnou
- Vždy verifikuj PO změně
- Loguj každou změnu (git commit nebo log file)
- Idempotentní pokud možno

## RELATED

- Skill `skill-creator` — vytváří nové skills
- Skill `{{related_skill}}` — {{related_description}}
