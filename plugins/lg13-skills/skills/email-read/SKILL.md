---
name: email-read
description: Use when the user wants to read, search, or check emails from seznam.cz or Outlook. Triggers on "zkontroluj maily", "přečti emaily", "hledej email od X", "co je v mailu", "nové zprávy", "email search", "inbox", "seznam mail", "outlook mail". Reads IMAP inbox, searches by sender/subject/keyword, returns summaries.
version: 1.0.0
---

# email-read — IMAP mail reader (seznam.cz + Outlook)

## PURPOSE

Číst a hledat emaily z seznam.cz a/nebo Outlook přes IMAP.
Token-efficient: vrátí jen souhrn (From, Subject, Date, snippet) — plný text na vyžádání.

---

## CONFIG

Credentials v `L:/LG13/runtime/secrets/email_secrets.json`:

```json
{
  "seznam": {
    "host": "imap.seznam.cz",
    "port": 993,
    "user": "tomas_kopecky@seznam.cz",
    "password": "<SEZNAM_PASS>"
  },
  "outlook": {
    "host": "outlook.office365.com",
    "port": 993,
    "user": "<OUTLOOK_EMAIL>",
    "password": "<OUTLOOK_PASS>"
  }
}
```

---

## EXECUTION

### 1. Read last N emails

```python
import imaplib, email, json, sys
from email.header import decode_header
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def decode_str(s):
    if not s: return ''
    parts = decode_header(s)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or 'utf-8', errors='replace'))
        else:
            result.append(str(part))
    return ''.join(result)

def read_inbox(account: str, limit: int = 10, unread_only: bool = False):
    secrets = json.loads(Path('L:/LG13/runtime/secrets/email_secrets.json').read_text(encoding='utf-8'))
    cfg = secrets[account]
    
    m = imaplib.IMAP4_SSL(cfg['host'], cfg['port'])
    m.login(cfg['user'], cfg['password'])
    m.select('INBOX')
    
    criteria = 'UNSEEN' if unread_only else 'ALL'
    _, ids = m.search(None, criteria)
    mail_ids = ids[0].split()[-limit:]  # last N
    
    results = []
    for mid in reversed(mail_ids):
        _, data = m.fetch(mid, '(RFC822.SIZE BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if data and data[0]:
            msg = email.message_from_bytes(data[0][1])
            results.append({
                'id': mid.decode(),
                'from': decode_str(msg.get('From', '')),
                'subject': decode_str(msg.get('Subject', '')),
                'date': msg.get('Date', ''),
            })
    m.logout()
    return results

# Usage:
msgs = read_inbox('seznam', limit=10, unread_only=False)
for m in msgs:
    print(f"[{m['date'][:16]}] {m['from'][:30]:<30} {m['subject'][:60]}")
```

### 2. Search emails

```python
def search_emails(account: str, query: str, field: str = 'ALL', limit: int = 20):
    """field: FROM, SUBJECT, BODY, TEXT, ALL"""
    secrets = json.loads(Path('L:/LG13/runtime/secrets/email_secrets.json').read_text(encoding='utf-8'))
    cfg = secrets[account]
    
    m = imaplib.IMAP4_SSL(cfg['host'], cfg['port'])
    m.login(cfg['user'], cfg['password'])
    m.select('INBOX')
    
    if field == 'ALL':
        criteria = f'TEXT "{query}"'
    else:
        criteria = f'{field} "{query}"'
    
    _, ids = m.search(None, criteria)
    mail_ids = ids[0].split()[-limit:]
    
    results = []
    for mid in reversed(mail_ids):
        _, data = m.fetch(mid, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if data and data[0]:
            msg = email.message_from_bytes(data[0][1])
            results.append({
                'id': mid.decode(),
                'from': decode_str(msg.get('From', '')),
                'subject': decode_str(msg.get('Subject', '')),
                'date': msg.get('Date', ''),
            })
    m.logout()
    return results

# Usage:
hits = search_emails('seznam', 'forpsi', field='FROM')
hits += search_emails('outlook', 'invoice', field='SUBJECT')
```

### 3. Read full email body

```python
def read_full(account: str, mail_id: str) -> str:
    secrets = json.loads(Path('L:/LG13/runtime/secrets/email_secrets.json').read_text(encoding='utf-8'))
    cfg = secrets[account]
    
    m = imaplib.IMAP4_SSL(cfg['host'], cfg['port'])
    m.login(cfg['user'], cfg['password'])
    m.select('INBOX')
    
    _, data = m.fetch(mail_id.encode(), '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or 'utf-8', errors='replace')
                break
    else:
        body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or 'utf-8', errors='replace')
    
    m.logout()
    return body[:3000]  # cap at 3k chars

# Usage:
body = read_full('seznam', '1234')
print(body)
```

---

## PARAMETRY (při invokaci)

| Parametr | Default | Příklad |
|----------|---------|---------|
| `account` | seznam | seznam / outlook / both |
| `limit` | 10 | počet emailů |
| `unread_only` | False | True = jen nepřečtené |
| `search` | — | hledaný text |
| `field` | ALL | FROM / SUBJECT / BODY |

---

## VÝSTUP

Výchozí: tabulka posledních N emailů (From, Subject, Date).
Na vyžádání: plný text emailu přes `read_full`.

---

## RULES

- **Nikdy nevypisuj hesla** — jen číst ze secrets souboru
- **Cap body na 3000 chars** — email může být obrovský
- **Unread first** — při `unread_only=True` zobrazit nejdřív
- Secrets file **nikdy necommitovat** do gitu

---

## RELATED

- Skill `tom-notify` — odesílání notifikací (ne příjem)
- Skill `tmonkey-web` — web scraping (ne email)
- Secrets: `L:/LG13/runtime/secrets/email_secrets.json`
