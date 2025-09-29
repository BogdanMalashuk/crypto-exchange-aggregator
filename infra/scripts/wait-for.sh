#!/bin/sh

set -e

hostport="$1"
timeout=${2:-30}

host=$(echo $hostport | cut -d: -f1)
port=$(echo $hostport | cut -d: -f2)

echo "Waiting for $host:$port..."

for i in $(seq 1 $timeout); do
  nc -z "$host" "$port" >/dev/null 2>&1 && break
  echo -n "."
  sleep 1
done

nc -z "$host" "$port" >/dev/null 2>&1 || {
  echo "Timeout waiting for $host:$port"
  exit 1
}

echo "$host:$port is available!"
