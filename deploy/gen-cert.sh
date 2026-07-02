#!/usr/bin/env bash
# Generate a self-signed TLS cert for local/staging use.
# For production: replace with Let's Encrypt or your CA-issued cert.
# Usage: bash deploy/gen-cert.sh [hostname]
#
# Output: deploy/certs/server.{crt,key}  (mounted into nginx container)
set -euo pipefail

HOST="${1:-localhost}"
CERT_DIR="$(dirname "$0")/certs"
mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout "$CERT_DIR/server.key" \
  -out    "$CERT_DIR/server.crt" \
  -subj   "/CN=$HOST" \
  -addext "subjectAltName=DNS:$HOST,DNS:localhost,IP:127.0.0.1"

chmod 600 "$CERT_DIR/server.key"
echo "✓ Self-signed cert written to $CERT_DIR/ (CN=$HOST, valid 365 days)"
echo "  For production, replace with: certbot certonly --standalone -d $HOST"
