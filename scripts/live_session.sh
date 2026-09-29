#!/usr/bin/env bash
# A live, typed session with the network off: you type help, status, ingest, search,
# ask, and chat yourself, and the whole terminal is recorded as evidence.
#
#   scripts/live_session.sh             wait until Wi-Fi is off, then open the session shell
#   scripts/live_session.sh --rehearse  skip the network wait (for testing the script)
#
# Saves evidence/live-session/transcript.txt (colours stripped, username redacted),
# terminal.typescript (raw recording) and runs/ (every ask/search/chat/ingest record).
# The shell uses a neutral prompt, so no username or computer name is recorded.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=evidence/live-session
online() { ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 || curl -s --max-time 3 -o /dev/null https://huggingface.co 2>/dev/null; }

if [ "${1:-}" != "--rehearse" ]; then
  [ -d "$OUT" ] && mv "$OUT" "$OUT-previous-$(date +%Y%m%d-%H%M%S)"
  while online; do
    printf '\r\033[33mNetwork is still up. Turn Wi-Fi off; the session opens by itself.\033[0m'; sleep 3
  done
  echo
fi
mkdir -p "$OUT"
export WIKI_RUNS_DIR="$PWD/$OUT/runs" BASH_SILENCE_DEPRECATION_WARNING=1

RC="$(mktemp)"
trap 'rm -f "$RC"' EXIT
cat > "$RC" <<'RCFILE'
PS1='\n\[\e[1;36m\]offline-demo \$\[\e[0m\] '
airgap() {
  echo "time:         $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "wi-fi:        $(networksetup -getairportpower en0 2>/dev/null || echo unknown)"
  ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 && echo "ping 1.1.1.1: REACHABLE" || echo "ping 1.1.1.1: blocked"
  curl -s --max-time 4 -o /dev/null https://huggingface.co && echo "HTTPS hf.co:  REACHABLE" || echo "HTTPS hf.co:  fails"
}
trap 'printf "\n\033[1;35m━━━ End of session: still offline? ━━━\033[0m\n"; airgap' EXIT
clear
printf '\033[1;35m━━━ Live session, typed by hand, offline ━━━\033[0m\n'
airgap
cat <<'STEPS'

Type these one at a time. Press Enter, and wait for the prompt to come back:

  1  ./wiki --help
  2  ./wiki status
  3  ./wiki ingest vault/raw --force        (Gemma re-drafts all 3 articles, about 30 s)
  4  ./wiki search "LIFO reserve"
  5  ./wiki ask "What was the total cost of sales for November under LIFO in the Foo Co. example?"
  6  ./wiki ask "Who founded the Save LIFO Coalition?"               (the notes don't say)
  7  ./wiki ask "In what year was the Save LIFO Coalition founded?"   (the notes don't say)
  8  ./wiki chat      then type:  what can we do?
                                  Summarize goodwill impairment in 3 bullets
                                  make that shorter
                                  /exit
  9  exit             (ends the recording and re-checks the network)
STEPS
RCFILE

script -q "$OUT/terminal.typescript" bash --noprofile --rcfile "$RC" -i

# Shareable transcript: strip colours; hide the Mac username in any file path.
perl -pe 's/\e\[[0-9;?]*[A-Za-z]//g; s/\e\][^\a]*\a//g; s/\r(?!\n)/\n/g; s/\r//g; s/\x04|\x08//g; s/^\^D//;
          s#/Users/[^/\s]+#/Users/<user>#g' "$OUT/terminal.typescript" > "$OUT/transcript.txt"
perl -pi -e 's#/Users/[^/\s]+#/Users/<user>#g' "$OUT/terminal.typescript"
echo
echo "Saved $OUT/transcript.txt and $OUT/runs/. You can turn Wi-Fi back on now."
