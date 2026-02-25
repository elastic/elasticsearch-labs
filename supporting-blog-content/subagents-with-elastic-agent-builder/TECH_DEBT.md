# Tech Debt Items

## AUTH-001: Token refresh race condition
- **Module**: src/auth/refresh.ts
- **Symptom**: Users randomly logged out
- **Estimate**: 3 days

## EXPORT-002: CSV export timeout on large datasets
- **Module**: src/export/csv.ts
- **Symptom**: Timeout after 30s for >10k rows
- **Estimate**: 2 days

## SEARCH-003: Indexing lag after bulk updates
- **Module**: src/search/indexer.ts
- **Symptom**: New products not searchable for ~5min
- **Estimate**: 5 days

## API-004: Rate limiter inconsistency
- **Module**: src/api/rate-limiter.ts
- **Symptom**: Some endpoints not rate limited
- **Estimate**: 1 day

## NOTIFY-005: Silent email failures
- **Module**: src/notifications/email.ts
- **Symptom**: Emails fail without alerting
- **Estimate**: 2 days

## CACHE-006: Redis connection pooling
- **Module**: src/cache/redis.ts
- **Symptom**: Occasional connection exhaustion
- **Estimate**: 3 days

## LOG-007: Inconsistent log levels
- **Module**: Multiple
- **Symptom**: Debug logs in production
- **Estimate**: 1 day

## DB-008: Missing database indexes
- **Module**: src/db/queries.ts
- **Symptom**: Slow queries on user table
- **Estimate**: 0.5 days

## TEST-009: Flaky integration tests
- **Module**: tests/integration/*
- **Symptom**: Random CI failures
- **Estimate**: 4 days

## UI-010: Memory leak in dashboard
- **Module**: src/components/Dashboard.tsx
- **Symptom**: Browser slowdown after 2hrs
- **Estimate**: 2 days

## SEC-011: Outdated dependencies
- **Module**: package.json
- **Symptom**: 3 moderate vulnerabilities
- **Estimate**: 1 day

## PERF-012: N+1 queries in reports
- **Module**: src/reports/generator.ts
- **Symptom**: Report generation slow
- **Estimate**: 2 days
