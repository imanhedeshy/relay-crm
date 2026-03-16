#!/usr/bin/env sh
set -eu

host="$1"
port="$2"

while ! nc -z "$host" "$port"; do
  sleep 1
done
