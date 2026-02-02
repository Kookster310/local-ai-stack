#!/bin/bash
# Git credential helper for GitHub App tokens
# Generates a fresh token on each git operation

# Read the request from git
while read line; do
    if [[ "$line" == "" ]]; then
        break
    fi
    
    case "$line" in
        protocol=*) protocol="${line#protocol=}" ;;
        host=*) host="${line#host=}" ;;
    esac
done

# Only handle github.com
if [[ "$host" != "github.com" ]]; then
    exit 0
fi

# Generate a fresh token
TOKEN=$(python3 /workspace/scripts/github-token.py 2>/dev/null)

if [[ -n "$TOKEN" ]]; then
    echo "protocol=https"
    echo "host=github.com"
    echo "username=x-access-token"
    echo "password=$TOKEN"
fi
