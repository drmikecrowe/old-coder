#!/bin/sh
# Fail-closed execution and completion accounting for the gauntlet entry point.
GAUNTLET_EXPECTED_LAYERS="orchestration-self-test checker-self-test source-state-self-test tests-coverage types lint-format shell-lint supply-chain must-not-scans mutation-control mutation real-execution source-state"
GAUNTLET_COMPLETED_LAYERS=""

# State the exit trap classifies from. run_layer and finish_gauntlet keep
# their own return statuses (the controls in test_gauntlet_orchestration.sh
# assert them); these variables only tell the trap WHY the script is exiting.
GAUNTLET_STAMP="${GAUNTLET_STAMP:-gauntlet-stamp.txt}"
GAUNTLET_SOURCE_STATE_CMD="${GAUNTLET_SOURCE_STATE_CMD:-tools/source_state.sh}"
GAUNTLET_FAILED_LAYER=""
GAUNTLET_FAILED_RC=""
GAUNTLET_ORCH_ERROR=""
GAUNTLET_AUDIT_PASSED=0

run_layer() {
  if [ "$#" -lt 2 ]; then
    GAUNTLET_ORCH_ERROR="run_layer requires a layer name and command"
    echo "FAIL: run_layer requires a layer name and command" >&2
    return 2
  fi

  layer=$1
  shift

  case " $GAUNTLET_EXPECTED_LAYERS " in
    *" $layer "*) ;;
    *)
      GAUNTLET_ORCH_ERROR="unknown layer '$layer'"
      echo "FAIL: unknown layer '$layer'" >&2
      return 2
      ;;
  esac

  case " $GAUNTLET_COMPLETED_LAYERS " in
    *" $layer "*)
      GAUNTLET_ORCH_ERROR="duplicate layer '$layer'"
      echo "FAIL: duplicate layer '$layer'" >&2
      return 2
      ;;
  esac

  printf '=== %s ===\n' "$layer"
  if "$@"; then
    GAUNTLET_COMPLETED_LAYERS="$GAUNTLET_COMPLETED_LAYERS $layer"
    return 0
  else
    rc=$?
    GAUNTLET_FAILED_LAYER=$layer
    GAUNTLET_FAILED_RC=$rc
    printf "FAIL: layer '%s' failed (rc=%s)\n" "$layer" "$rc" >&2
    return "$rc"
  fi
}

finish_gauntlet() {
  missing_layers=""
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    case " $GAUNTLET_COMPLETED_LAYERS " in
      *" $layer "*) ;;
      *)
        echo "FAIL: missing layer '$layer'" >&2
        missing_layers="$missing_layers $layer"
        ;;
    esac
  done

  if [ -n "$missing_layers" ]; then
    GAUNTLET_ORCH_ERROR="missing layer(s):$missing_layers"
    return 1
  fi
  GAUNTLET_AUDIT_PASSED=1
  echo "=== gauntlet: all layers green ==="
}

# Classifies the finished run. One function serves both the stamp and the
# exit remap, so the two cannot disagree.
gauntlet_result() {
  status=$1
  if [ "$status" -eq 0 ] && [ "$GAUNTLET_AUDIT_PASSED" -eq 1 ]; then
    echo "green"
  elif [ "$status" -eq 0 ]; then
    echo "incomplete (exited 0 before the completion audit)"
  elif [ -n "$GAUNTLET_ORCH_ERROR" ]; then
    echo "orchestration-error ($GAUNTLET_ORCH_ERROR)"
  elif [ -n "$GAUNTLET_FAILED_LAYER" ]; then
    echo "layer-failed ($GAUNTLET_FAILED_LAYER, rc=$GAUNTLET_FAILED_RC)"
  else
    echo "crash (rc=$status)"
  fi
}

# The completion stamp: the harness-written record of what this run proved,
# written on every exit path. The green result comes only from the final
# audit, and the source binding comes only from the source-state command —
# where that command fails, the stamp says unavailable rather than guessing.
write_gauntlet_stamp() {
  result=$1
  {
    echo "result: $result"
    echo "finished_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "expected_layers: $GAUNTLET_EXPECTED_LAYERS"
    echo "completed_layers:${GAUNTLET_COMPLETED_LAYERS:- none}"
    if state=$("$GAUNTLET_SOURCE_STATE_CMD" 2>&1); then
      printf '%s\n' "$state" | sed 's/^/source_state: /'
    else
      echo "source_state: unavailable ($GAUNTLET_SOURCE_STATE_CMD failed)"
    fi
  } > "$GAUNTLET_STAMP"
}

# Exit vocabulary: 0 all layers green; 2 a layer ran and failed (its own
# status is preserved in the stamp); 3 the orchestration contract was
# violated, including an exit 0 that never reached the audit; any other
# status is a crash, passed through unchanged.
gauntlet_exit_trap() {
  status=$?
  result=$(gauntlet_result "$status")
  write_gauntlet_stamp "$result"
  case "$result" in
    green) exit 0 ;;
    layer-failed*) exit 2 ;;
    orchestration-error*|incomplete*) exit 3 ;;
    *) exit "$status" ;;
  esac
}

install_gauntlet_exit_trap() {
  trap gauntlet_exit_trap EXIT
}
