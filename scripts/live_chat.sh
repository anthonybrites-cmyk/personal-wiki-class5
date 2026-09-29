#!/usr/bin/env bash
# A live, typed chat session with the network off, recorded as evidence.
#
#   scripts/live_chat.sh             wait until Wi-Fi is off, then open `wiki chat` for you to type in
#   scripts/live_chat.sh --rehearse  skip the network wait (for testing the script)
#
# Saves evidence/live-chat/transcript.txt (colours stripped, username/hostname redacted),
# terminal.typescript (raw recording) and runs/chat/<time>-session.{md,json}.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=evidence/live-chat
online() { ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 || curl -s --max-time 3 -o /dev/null https://huggingface.co 2>/dev/null; }
airgap() {
  echo "time:         $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "wi-fi:        $(networksetup -getairportpower en0 2>/dev/null || echo unknown)"
  ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 && echo "ping 1.1.1.1: REACHABLE" || echo "ping 1.1.1.1: blocked"
  curl -s --max-time 4 -o /dev/null https://huggingface.co && echo "HTTPS hf.co:  REACHABLE" || echo "HTTPS hf.co:  fails"
}

if [ "${1:-}" != "--rehearse" ]; then
  [ -d "$OUT" ] && mv "$OUT" "$OUT-previous-$(date +%Y%m%d-%H%M%S)"
  while online; do
    printf '\r\033[33mNetwork is still up. Turn Wi-Fi off; the chat opens by itself.\033[0m'; sleep 3
  done
  echo
fi
mkdir -p "$OUT"
export WIKI_RUNS_DIR="$PWD/$OUT/runs" OUT
script -q "$OUT/terminal.typescript" bash -c '
  clear
  printf "\033[1;35m━━━ Live chat, offline ━━━\033[0m\n"
  '"$(declare -f airgap)"'
  airgap
  printf "\n\033[1;36m$ ./wiki chat\033[0m\n"
  ./wiki chat
  printf "\n\033[1;35m━━━ After the chat ━━━\033[0m\n"
  airgap
'
# Clean, shareable transcript: strip colours; hide the Mac username and computer name.
perl -pe 's/\e\[[0-9;?]*[A-Za-z]//g; s/\r(?!\n)/\n/g; s/\r//g; s/\x04|\x08//g; s/^\^D//;
          s#/Users/[^/\s]+#/Users/<user>#g' "$OUT/terminal.typescript" > "$OUT/transcript.txt"
perl -pi -e 's#/Users/[^/\s]+#/Users/<user>#g' "$OUT/terminal.typescript"
echo
echo "Saved $OUT/transcript.txt and $OUT/runs/chat/. You can turn Wi-Fi back on now."
