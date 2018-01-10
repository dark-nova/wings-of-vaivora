#!/usr/bin/env bash

file="version.json"

# modified from: https://stackoverflow.com/a/677212
type python > /dev/null 2>&1 || exit
# end

[ -f "$file" ] || exit

# modified from: https://stackoverflow.com/a/32228333
out=$(cat "$file" | python -m json.tool)
echo "$out" > "$file"