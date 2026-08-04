#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose up -d --wait db

query() {
  docker compose exec -T db psql \
    -X -A -t -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$1" \
    | tr -d '[:space:]'
}

assert_equals() {
  local expected="$1"
  local sql="$2"
  local label="$3"
  local actual
  actual="$(query "$sql")"
  if [ "$actual" != "$expected" ]; then
    echo "Database verification failed: $label (expected $expected, got $actual)" >&2
    exit 1
  fi
  echo "OK: $label"
}

assert_equals "1" "SELECT count(*) FROM pg_extension WHERE extname = 'vector';" "pgvector extension"
assert_equals "1" "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents';" "documents table"
assert_equals "1" "SELECT count(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'embedding' AND udt_name = 'vector';" "vector column"
assert_equals "1" "SELECT count(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'fts' AND is_generated = 'ALWAYS';" "generated full-text column"
assert_equals "1" "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'documents' AND indexdef ILIKE '%USING hnsw%';" "HNSW index"
assert_equals "1" "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'documents' AND indexdef ILIKE '%USING gin%';" "GIN index"
assert_equals "1" "SELECT count(*) FROM pg_proc WHERE proname = 'hybrid_search';" "hybrid search function"
assert_equals "1" "SELECT CASE WHEN count(*) > 0 THEN 1 ELSE 0 END FROM hybrid_search('PostgreSQL', ('[' || array_to_string(array_fill(0.0::double precision, ARRAY[1536]), ',') || ']')::vector, 5);" "hybrid search execution"

document_count="$(query "SELECT count(*) FROM documents;")"
if ! [[ "$document_count" =~ ^[0-9]+$ ]] || [ "$document_count" -lt 1 ]; then
  echo "Database verification failed: expected at least one seed row, got $document_count" >&2
  exit 1
fi
echo "OK: seed rows ($document_count)"

echo "Database verification passed without calling an external API."
