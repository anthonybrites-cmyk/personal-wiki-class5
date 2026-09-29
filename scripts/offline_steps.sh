#!/usr/bin/env bash
# The steps of the offline demo (run by scripts/offline_demo.sh inside script(1)).
# Each `./wiki` below is a new process started after the network went down.
set -uo pipefail
cd "$ROOT"
export WIKI_RUNS_DIR="$ROOT/$OUT/runs"
[ "${OUT#/}" != "$OUT" ] && export WIKI_RUNS_DIR="$OUT/runs"  # absolute OUT (rehearsal)
MEAS="$(dirname "$WIKI_RUNS_DIR")/measurements.tsv"
printf 'step\twall_s\tmax_rss_gb\tpeak_footprint_gb\n' > "$MEAS"

banner() { printf '\n\033[1;35m━━━ %s ━━━\033[0m\n' "$*"; }
show()   { printf '\n\033[1;36m$ %s\033[0m\n' "$*"; }

# Run a command under /usr/bin/time -l and log wall time and memory.
measured() {
  local label="$1"; shift
  local t; t="$(mktemp)"
  show "$*"
  /usr/bin/time -l -o "$t" "$@"
  local rc=$?
  local wall rss peak
  wall=$(awk '/ real /{print $1}' "$t")
  rss=$(awk '/maximum resident set size/{printf "%.2f", $1/1e9}' "$t")
  peak=$(awk '/peak memory footprint/{printf "%.2f", $1/1e9}' "$t")
  printf '\033[2m[measured: %s s wall · max RSS %s GB · peak memory footprint %s GB]\033[0m\n' "$wall" "$rss" "$peak"
  printf '%s\t%s\t%s\t%s\n' "$label" "$wall" "$rss" "$peak" >> "$MEAS"
  rm -f "$t"
  return $rc
}

airgap() {
  echo "time:            $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "wi-fi:           $(networksetup -getairportpower en0 2>/dev/null || echo unknown)"
  if route -n get default >/dev/null 2>&1; then
    echo "default route:   PRESENT via $(route -n get default 2>/dev/null | awk '/interface:/{print $2}')"
  else
    echo "default route:   none (no path off this machine)"
  fi
  ping -c 1 -t 2 1.1.1.1 >/dev/null 2>&1 && echo "ping 1.1.1.1:    REACHABLE" || echo "ping 1.1.1.1:    blocked"
  nslookup huggingface.co >/dev/null 2>&1 && echo "DNS hf.co:       RESOLVES" || echo "DNS hf.co:       fails"
  curl -s --max-time 4 -o /dev/null https://huggingface.co && echo "HTTPS hf.co:     REACHABLE" || echo "HTTPS hf.co:     fails"
}

banner "1. Proof the machine is offline"
airgap

banner "2. Device and runtime"
show "system_profiler SPHardwareDataType | grep -E 'Model Name|Chip|Total Number of Cores|Memory'"
system_profiler SPHardwareDataType 2>/dev/null | grep -E 'Model Name|Chip|Total Number of Cores|Memory'
show "sw_vers; df -h /; memory_pressure | tail -1"
sw_vers
df -h / | tail -1 | awk '{print "free disk: " $4 " of " $2}'
memory_pressure 2>/dev/null | tail -1
show ".venv/bin/python -c 'import mlx.core, mlx_vlm, mlx_embeddings, platform; ...'"
.venv/bin/python -c "import mlx.core as mx, mlx_vlm, platform, importlib.metadata as m; print('python', platform.python_version(), '| mlx', mx.__version__, '| mlx-vlm', mlx_vlm.__version__, '| mlx-embeddings', m.version('mlx-embeddings'), '| metal', mx.metal.is_available())"

banner "3. Help and status (fresh CLI process)"
show "./wiki --help"
./wiki --help
show "./wiki status"
./wiki status

banner "4. Conversion and ingestion with local Gemma"
show "./wiki convert --force   # .txt originals -> Markdown, word sequence verified, originals untouched"
./wiki convert --force
show "shasum -a 256 vault/raw/*.txt   # compare with tests/original-txt-sha256.txt"
shasum -a 256 vault/raw/*.txt | sed 's|vault/raw/||' | diff - tests/original-txt-sha256.txt && echo "originals unchanged: all 3 hashes match the ones recorded before processing"
show ".venv/bin/python scripts/reingest_check.py $OUT/reingest-check.md vault/raw   # runs ./wiki ingest vault/raw --force under /usr/bin/time"
MEAS_FILE="$MEAS" .venv/bin/python scripts/reingest_check.py "$(dirname "$WIKI_RUNS_DIR")/reingest-check.md" vault/raw

show ".venv/bin/python scripts/check_links.py   # every [[link]] and #heading in the vault resolves"
.venv/bin/python scripts/check_links.py "$(dirname "$WIKI_RUNS_DIR")/link-check.md"

banner "5. Search mode: original passages only, no model"
measured "search" ./wiki search "LIFO reserve" -k 3
show "./wiki search \"price protection for shareholders\" -k 3"
./wiki search "price protection for shareholders" -k 3

banner "6. Ask mode: the four pre-registered tests (tests/ask-tests.md)"
measured "ask test-1" ./wiki ask "In the Foo Co. example, what was the total cost of sales for November under FIFO?" --mode local
measured "ask test-2" ./wiki ask "Can a company count the customer loyalty it built up by itself as something it owns on its books?" --mode local
measured "ask test-3" ./wiki ask "What does goodwill represent in an acquisition, and which kind of contingent value right protects the buyer against overpaying?" --mode local
measured "ask test-4" ./wiki ask "What discount rate must companies use when testing goodwill for impairment?" --mode local

banner "7. Chat mode checks: capabilities, a plan, a follow-up, and a claim made only in chat"
show "printf '...' | ./wiki chat     (scripted input, echoed below as you>)"
printf '%s\n' \
  "what can we do?" \
  "what can you help me with?" \
  "Draft a short study plan for learning goodwill accounting." \
  "make that shorter" \
  "By the way, my professor told me LIFO is allowed under IFRS." \
  "/exit" | ./wiki chat

banner "8. Ask is independent of chat: the claim made in chat is not evidence"
measured "ask after chat" ./wiki ask "Is LIFO allowed under IFRS?" --mode local --quiet

banner "9. Still offline at the end?"
airgap
