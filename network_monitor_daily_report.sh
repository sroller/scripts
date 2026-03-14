#!/bin/bash

LOG_DIR=/var/log/network_monitor
LOG_FILE=$LOG_DIR/network_monitor2.log
DATE=$(date +%Y%m%d)
OUTAGE_TRACKER=$LOG_DIR/outages_${DATE}.tracker

# Email address - override via command line argument
EMAIL_TO="${1:-}"

if [ -z "$EMAIL_TO" ]; then
    echo "Usage: $0 <email_address>" >&2
    exit 1
fi

# Check if there were any outages today
if [ -f "$OUTAGE_TRACKER" ] && [ -s "$OUTAGE_TRACKER" ]; then
    # Count outages and calculate total downtime
    OUTAGE_COUNT=$(wc -l < "$OUTAGE_TRACKER")
    TOTAL_DOWNTIME=$(awk '{sum+=$1} END {print sum}' "$OUTAGE_TRACKER")

    # Get longest outage
    LONGEST=$(sort -n "$OUTAGE_TRACKER" | tail -1)

    # Generate timeline from log file
    TIMELINE=$(grep "Connection restored after" "$LOG_FILE" | tail -10 | sed 's/^/  /')

    # Generate email body with outage timeline
    cat << EOF | mail -s "Network Outage Report for $(date +%Y-%m-%d)" "$EMAIL_TO"
Network Outage Report - $(date +%Y-%m-%d)

Summary:
  Total outages: $OUTAGE_COUNT
  Total downtime: ${TOTAL_DOWNTIME} seconds
  Longest outage: ${LONGEST} seconds

Outage Timeline (last 10):
$TIMELINE

Log file: $LOG_DIR/network_monitor2.log
EOF
fi
