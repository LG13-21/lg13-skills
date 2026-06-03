---
name: ftp
description: FTP upload/download/list na ftpx.forpsi.com (luky.ai-domy.cz). Trigger: "/ftp upload", "/ftp ls", "/ftp download", "nahraj na server", "stáhni ze serveru", "co je na FTP", "deploy na web". Credentials z L:/LG13/runtime/secrets/ftp_secrets.json.
version: 1.0.0
---

# ftp — FTP operace na Forpsi / luky.ai-domy.cz

## SPUŠTĚNÍ

```
/ftp ls /subdoms/luky/web_up/
/ftp upload L:/soubor.php /subdoms/luky/api/
/ftp sync L:/GitHub/legal-ship-2026/F25 /subdoms/luky/web_up/ --ext .pdf .zip .html

# Nebo přes skill_io (request/response JSON + denní log):
python skill_io.py --run ftp '{"op":"ls","path":"/subdoms/luky/web_up"}'
python skill_io.py --run ftp '{"op":"upload","local":"L:/soubor.php","remote_dir":"/subdoms/luky/api"}'
python skill_io.py --log-tail 10
/ftp upload L:/GitHub/legal-ship-2026/F25/index.html /subdoms/luky/web_up/
/ftp upload L:/GitHub/ai-domy-cz/subdoms/luky/api/config.php /subdoms/luky/api/
/ftp download /subdoms/luky/api/config.php /tmp/config_server.php
```

## IMPLEMENTACE

```python
import ftplib, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FTP_SECRETS = json.loads(Path('L:/LG13/runtime/secrets/ftp_secrets.json').read_text(encoding='utf-8'))
cfg = FTP_SECRETS['forpsi']

def ftp_connect():
    ftp = ftplib.FTP_TLS()
    ftp.connect(cfg['host'], cfg['port'], timeout=30)
    ftp.login(cfg['user'], cfg['password'])
    ftp.prot_p()
    return ftp

# --- LIST ---
def ftp_ls(remote_path: str):
    ftp = ftp_connect()
    ftp.cwd(remote_path)
    lines = []
    ftp.retrlines('LIST', lines.append)
    ftp.quit()
    for l in lines:
        print(l)

# --- UPLOAD jednoho souboru ---
def ftp_upload(local_path: str, remote_dir: str, remote_name: str = None):
    lp = Path(local_path)
    remote_name = remote_name or lp.name
    ftp = ftp_connect()
    ftp.cwd(remote_dir)
    with open(lp, 'rb') as f:
        ftp.storbinary(f'STOR {remote_name}', f)
    ftp.quit()
    size_kb = round(lp.stat().st_size / 1024, 1)
    print(f'UPLOAD OK: {lp.name} → {remote_dir}/{remote_name} ({size_kb} KB)')

# --- UPLOAD adresáře (recursive) ---
def ftp_upload_dir(local_dir: str, remote_dir: str, extensions=None):
    ld = Path(local_dir)
    ftp = ftp_connect()
    ftp.cwd(remote_dir)
    uploaded = 0
    for fp in sorted(ld.iterdir()):
        if fp.is_file():
            if extensions and fp.suffix.lower() not in extensions:
                continue
            with open(fp, 'rb') as f:
                ftp.storbinary(f'STOR {fp.name}', f)
            print(f'  OK {fp.name} ({round(fp.stat().st_size/1024,1)} KB)')
            uploaded += 1
    ftp.quit()
    print(f'UPLOAD DIR OK: {uploaded} souborů → {remote_dir}')

# --- DOWNLOAD ---
def ftp_download(remote_path: str, local_path: str):
    import io
    ftp = ftp_connect()
    remote_dir = '/'.join(remote_path.split('/')[:-1])
    remote_file = remote_path.split('/')[-1]
    ftp.cwd(remote_dir)
    buf = io.BytesIO()
    ftp.retrbinary(f'RETR {remote_file}', buf.write)
    ftp.quit()
    Path(local_path).write_bytes(buf.getvalue())
    print(f'DOWNLOAD OK: {remote_path} → {local_path} ({round(len(buf.getvalue())/1024,1)} KB)')

# Příklad použití (nahradit dle potřeby):
# ftp_ls('/subdoms/luky/web_up')
# ftp_upload('L:/soubor.pdf', '/subdoms/luky/web_up')
# ftp_upload_dir('L:/GitHub/legal-ship-2026/F25', '/subdoms/luky/web_up', {'.pdf','.zip','.html'})
# ftp_download('/subdoms/luky/api/config.php', 'C:/tmp/config.php')
```

## CONFIG

Credentials: `L:/LG13/runtime/secrets/ftp_secrets.json`

```json
{
  "forpsi": {
    "host": "ftpx.forpsi.com",
    "port": 21,
    "user": "www.ai-domy.cz",
    "password": "FhnLnN2kRc",
    "tls": true,
    "web_root": "/subdoms/luky"
  }
}
```

## ČASTÉ CESTY NA SERVERU

| Cesta | Obsah |
|-------|-------|
| `/subdoms/luky/` | Kořen luky.ai-domy.cz |
| `/subdoms/luky/api/` | PHP API (db_proxy, config, ingest...) |
| `/subdoms/luky/web_up/` | Review web pro Toma (F-cykly) |
| `/subdoms/luky/config.php` | DB + API klíče (parent config pro api/) |
| `/www/` | Hlavní web ai-domy.cz |

## BEZPEČNOST

- Nikdy nevypisuj FTP heslo v logu
- Vždy použij FTP_TLS + prot_p() (šifrovaný přenos dat)
- Po každé operaci volej ftp.quit()
