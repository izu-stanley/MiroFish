#!/usr/bin/env bash
#
# MiroFish CLI trigger - Run the full pipeline in your terminal.
# Uses your local Cursor Agent (must be logged in: agent login).
#
# Usage: ./run.sh <project_dir> -r "requirement" [options]
#   -r, --requirement   Simulation requirement (required)
#   --name              Project name (optional)
#   --max-rounds        Max simulation rounds (optional)
#   -o, --output        Write report to file in project dir (optional)
#
set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

usage() {
    cat <<EOF
Usage: $(basename "$0") <project_dir> -r "requirement" [options]

Run the MiroFish pipeline in your terminal. Uses your local Cursor Agent (agent login).

Arguments:
  project_dir          Directory containing seed files (.md, .txt, .pdf)

Options:
  -r, --requirement    Simulation requirement description (required)
  --name NAME          Project name (optional)
  --max-rounds N       Max simulation rounds (optional)
  -o, --output FILE    Write report to FILE in project dir (optional)

Examples:
  ./run.sh ./my-project -r "Predict campus event outcomes"
  ./run.sh . -r "Simulate social media response" -o report.md

Prerequisites: Node, Python 3.11+, uv, Cursor Agent (agent login). Run: npm run setup:all
EOF
    exit 1
}

# Portable absolute path (works on macOS without realpath)
abs_path() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        echo "Error: $dir is not a directory" >&2
        exit 1
    fi
    (cd "$dir" && pwd -P)
}

# Parse arguments
PROJECT_DIR=""
REQUIREMENT=""
PROJECT_NAME=""
MAX_ROUNDS=""
OUTPUT_FILE=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -r|--requirement)
            REQUIREMENT="$2"
            shift 2
            ;;
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --max-rounds)
            MAX_ROUNDS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        --seed-file)
            EXTRA_ARGS+=("--seed-file" "$2")
            shift 2
            ;;
        -*)
            echo "Error: Unknown option $1" >&2
            usage
            ;;
        *)
            if [[ -z "$PROJECT_DIR" ]]; then
                PROJECT_DIR="$1"
            else
                EXTRA_ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

if [[ -z "$PROJECT_DIR" ]]; then
    PROJECT_DIR="."
fi

if [[ -z "$REQUIREMENT" ]]; then
    echo "Error: -r/--requirement is required" >&2
    usage
fi

ABSOLUTE_PROJECT_DIR="$(abs_path "$PROJECT_DIR")"

# Build CLI args (runs locally, uses your Cursor Agent)
CLI_ARGS=("$ABSOLUTE_PROJECT_DIR" "-r" "$REQUIREMENT")
[[ -n "$PROJECT_NAME" ]] && CLI_ARGS+=("--name" "$PROJECT_NAME")
[[ -n "$MAX_ROUNDS" ]] && CLI_ARGS+=("--max-rounds" "$MAX_ROUNDS")
if [[ -n "$OUTPUT_FILE" ]]; then
    # Resolve -o to absolute path in project dir so report lands where expected
    OUTPUT_PATH="${ABSOLUTE_PROJECT_DIR}/${OUTPUT_FILE#./}"
    CLI_ARGS+=("-o" "$OUTPUT_PATH")
fi
CLI_ARGS+=("${EXTRA_ARGS[@]}")

VENV_ACTIVATE="$SCRIPT_DIR/backend/.venv/bin/activate"
if [[ ! -f "$VENV_ACTIVATE" ]]; then
    echo "Error: venv not found. Run: cd backend && uv venv --python 3.12 && uv sync --python 3.12" >&2
    exit 1
fi
source "$VENV_ACTIVATE"

LOG_FILE="${ABSOLUTE_PROJECT_DIR}/pipeline_$(date +%Y%m%d_%H%M%S).log"
echo "Logging output to $LOG_FILE"
python "$SCRIPT_DIR/mirofish_cli.py" "${CLI_ARGS[@]}" 2>&1 | tee "$LOG_FILE"
