#!/bin/bash
# sas_retry_wrapper.sh -- retry SAS invocation on kernel-init failures (exit 112)
#
# Upload to WRDS home; use in qsub as:
#   qsub -v SAS_FILE=mysas.sas -o out.txt -e err.txt wrapped.sh
# where wrapped.sh calls:
#   source /gridware/sge/default/common/settings.sh
#   ~/sas_retry_wrapper.sh $SAS_FILE
#
# Or (simpler) inline in qsub:
#   echo "source /gridware/sge/default/common/settings.sh; ~/sas_retry_wrapper.sh ~/mysas.sas" | qsub -S /bin/bash -cwd -o out.txt -e err.txt -N myname
#
# Retry policy:
#   - exit 0,1,2 (success / SAS warnings / SAS errors): passthrough, no retry
#   - exit 112 (SAS kernel resource init failure): retry up to 3 times with 60s backoff
#   - any other exit: retry up to 2 times (could be transient too)
# Transient failures on WRDS are almost always node-specific SAS license/init races.

SAS_FILE="$1"
MAX_RETRIES=3
SLEEP_BETWEEN=60

if [ -z "$SAS_FILE" ]; then
  echo "Usage: $0 <sas_file>" >&2
  exit 64
fi

for attempt in $(seq 1 $MAX_RETRIES); do
  echo "[$(date)] attempt $attempt/$MAX_RETRIES: sas $SAS_FILE"
  sas "$SAS_FILE"
  rc=$?
  echo "[$(date)] attempt $attempt exit rc=$rc"

  case $rc in
    0|1|2)
      # 0 = success; 1 = warnings; 2 = SAS errors (log exists, user can inspect)
      echo "[$(date)] terminal success/SAS-error rc=$rc; not retrying"
      exit $rc
      ;;
    112)
      echo "[$(date)] SAS kernel init failure (exit 112); retrying after ${SLEEP_BETWEEN}s"
      ;;
    *)
      echo "[$(date)] unexpected rc=$rc; retrying once after ${SLEEP_BETWEEN}s"
      ;;
  esac

  if [ "$attempt" -lt "$MAX_RETRIES" ]; then
    sleep $SLEEP_BETWEEN
  fi
done

echo "[$(date)] exhausted $MAX_RETRIES retries; last rc=$rc"
exit $rc
