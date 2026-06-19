#!/bin/bash
# sync-db.sh — מריצים מהמק של דור: מעלה את osint.db המקומי ל-VM ומאתחל את הקונטיינר.
# שימוש: ./sync-db.sh   (או עם override: VM_HOST=... LOCAL_DB=... ./sync-db.sh)
set -euo pipefail

# ====== ערכו כאן (או דרכו במשתני סביבה) ======
VM_HOST="${VM_HOST:-dor@osint-vm.example.com}"   # user@host של ה-VM
VM_PATH="${VM_PATH:-/opt/osint-db}"               # התיקייה ב-VM שבה docker-compose.yml
LOCAL_DB="${LOCAL_DB:-$HOME/Documents/osint/osint.db}"  # הקובץ המקומי
# =============================================

if [ ! -s "$LOCAL_DB" ]; then
  echo "error: local DB not found or empty: $LOCAL_DB" >&2
  exit 1
fi

echo "uploading $LOCAL_DB -> $VM_HOST:$VM_PATH/osint.db.new"
scp "$LOCAL_DB" "$VM_HOST:$VM_PATH/osint.db.new"

echo "swapping DB atomically and restarting container"
ssh "$VM_HOST" "mv '$VM_PATH/osint.db.new' '$VM_PATH/osint.db' && cd '$VM_PATH' && docker compose restart osint-db"

echo "done — osint-db is serving the fresh database."
