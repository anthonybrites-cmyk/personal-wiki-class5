#!/usr/bin/env bash
# Offline demonstration for the grader.
#
#   scripts/offline_demo.sh            wait until the network is down, then run everything
#   scripts/offline_demo.sh --rehearse run now even if online, into a scratch folder
#
# Every step starts a fresh `./wiki` process after the network is gone. Outputs:
#   evidence/offline/transcript.txt     full terminal transcript (ANSI colours stripped)
#   evidence/offline/terminal.typescript raw recording from script(1), with colours
#   evidence/offline/runs/              saved records from every ask/search/chat/ingest
#   evidence/offline/reingest-check.md  duplicate / rename check around offline ingestion
#   evidence/offline/measurements.tsv   wall time and memory for ingest and each ask
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"

online() {
  ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 && return 0
  curl -s --max-time 3 -o /dev/null https://huggingface.co 2>/dev/null
}

if [ "${1:-}" = "--rehearse" ]; then
  OUT="${REHEARSE_OUT:-${TMPDIR:-/tmp}/wiki-offline-rehearsal}"
  rm -rf "$OUT"
  echo "REHEARSAL (network not checked) → $OUT"
else
  OUT="evidence/offline"
  if [ -d "$OUT" ]; then  # never overwrite evidence: keep the previous run beside it
    mv "$OUT" "$OUT-previous-$(date +%Y%m%d-%H%M%S)"
  fi
  while online; do
    printf '\r\033[33mNetwork is still up. Turn Wi-Fi off (and unplug Ethernet); the demo starts by itself.\033[0m'
    sleep 3
  done
  printf '\n\033[32mNetwork is down. Starting the offline demo.\033[0m\n'
fi
mkdir -p "$OUT/runs"

# Record the whole run: script(1) shows it live and keeps a copy with colours.
script -q "$OUT/terminal.typescript" env OUT="$OUT" ROOT="$ROOT" scripts/offline_steps.sh
status=$?
perl -pe 's/\e\[[0-9;?]*[A-Za-z]//g; s/\r(?!\n)/\n/g; s/\r//g; s/\x04|\x08//g; s/^\^D//' \
  "$OUT/terminal.typescript" > "$OUT/transcript.txt"
echo
echo "Saved: $OUT/transcript.txt, $OUT/runs/, $OUT/reingest-check.md, $OUT/measurements.tsv"

if [ "${1:-}" != "--rehearse" ]; then
  printf '\033[1;32mOffline demo finished (exit %s). You can turn Wi-Fi back on now.\033[0m\n' "$status"
fi
exit $status
