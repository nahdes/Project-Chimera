#!/bin/bash

# Configuration
OAUTH_SERVER="https://mcppulse.10academy.org"
LOCAL_SERVER="http://localhost:3000"
CURL_TIMEOUT=10
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/health-check.log"

# Tracking
TESTS_PASSED=0
TESTS_FAILED=0

# ===== Utility Functions =====

log_message() {
    local message="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}" | tee -a "$LOG_FILE"
}

check_dependencies() {
    local missing_deps=0
    for cmd in curl jq; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: Required command '$cmd' not found"
            missing_deps=$((missing_deps + 1))
        fi
    done
    return $missing_deps
}

test_http_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    
    log_message "Testing: $name"
    
    local response
    local http_code
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -o /tmp/response.json \
            --max-time "$CURL_TIMEOUT" -X POST "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -o /tmp/response.json \
            --max-time "$CURL_TIMEOUT" "$url" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        log_message "  ✓ $name successful (HTTP 200)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_message "  ✗ $name failed (HTTP $http_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

test_oauth_metadata() {
    local name="$1"
    local url="$2"
    
    log_message "Testing: $name"
    
    local response
    if ! response=$(curl -s --max-time "$CURL_TIMEOUT" "$url" 2>/dev/null); then
        log_message "  ✗ $name failed (connection error)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    
    if ! echo "$response" | jq -e '.issuer' &>/dev/null; then
        log_message "  ✗ $name failed (invalid JSON or missing issuer)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    
    local issuer=$(echo "$response" | jq -r '.issuer')
    log_message "  ✓ $name successful - Issuer: $issuer"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
}

print_summary() {
    local total=$((TESTS_PASSED + TESTS_FAILED))
    
    echo ""
    log_message "=== Test Summary ==="
    log_message "Total: $total | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_message "✓ All tests passed"
        return 0
    else
        log_message "✗ Some tests failed"
        return 1
    fi
}

# ===== Main Execution =====

log_message "Starting OAuth Server Health Check"

if ! check_dependencies; then
    log_message "Error: Missing required dependencies"
    exit 1
fi

log_message "=== OAuth Metadata Checks ==="
test_oauth_metadata "OAuth Authorization Server Metadata" \
    "$OAUTH_SERVER/.well-known/oauth-authorization-server"

log_message ""
log_message "=== Connectivity Checks ==="
test_http_endpoint "Token Endpoint" "$OAUTH_SERVER/token" "POST"
test_http_endpoint "Local MCP Health" "$LOCAL_SERVER/health" "GET"

log_message ""
print_summary
FINAL_STATUS=$?

log_message "Health check complete"
exit $FINAL_STATUS
