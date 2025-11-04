#!/bin/bash
set -e
this="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../"
cd "$this" || { echo "no such dir $this"; exit 1; }

# get branch name
curBranch=$(git rev-parse --abbrev-ref HEAD)

# git pull
git_output=$(git pull 2>&1)

#
if echo "$git_output" | grep -q "Already up to date."; then
    echo "no change, skip"
    exit 0
fi

if echo "$git_output" | grep -q "Updating"; then
    if ! echo "$git_output" | grep -q "$curBranch"; then
        echo "no valid update in current branch $curBranch, skip"
        exit 1
    fi
    echo "changes pulled, about to apply"
fi

echo "unexpected git pull response:"
echo "$git_output"
exit 1
