---
name: backend-log-contract-trace
description: Trace backend logs to the exact code path and contract boundary across API routes, controller methods, request parameters, DTO/VO classes, entity fields, service calls, MyBatis mapper interfaces/XML, SQL column names, cross-service payloads, and database constraints. Use when debugging ToolFlow/app-model-style backend failures, ORM/MyBatis errors, SQL exceptions, 404/NPE/publish/download failures, enum or field-length violations, mismatched request/response contracts, or when the user asks to verify a fix was not rolled back by re-opening current files before and after changes.
---

# Backend Log Contract Trace

## Overview

Use this skill to turn backend logs into a verified code-and-contract trace. The goal is to answer from the current repository, not memory: identify the real endpoint, method, DTO/VO, entity, mapper XML, SQL, downstream call, and database constraint involved.

## Workflow

1. Capture the exact failure signal.
   - Preserve the log timestamp, request path, HTTP method, exception class, stack frames, SQL error code, parameter values, trace ID, and response body when present.
   - If the user asks whether a fix was rolled back, treat that as a live-file verification task.
2. Re-open current files before making claims.
   - Inspect the controller/router, service, mapper interface, mapper XML, DTO/VO, entity, enum, and config files currently on disk.
   - Do not rely on previous memory of the codebase unless it has been rechecked in this turn.
3. Map the entrypoint.
   - Search by request path, controller annotation, method name, stack frame class, log message, error code, or SQL fragment.
   - Record the concrete route and method, including path variables, query parameters, body object, and validation annotations.
4. Follow the contract chain.
   - API request: parameter names, JSON field names, required/nullability rules, enum values, defaulting, and type conversions.
   - DTO/VO: serialization names, validation annotations, nested objects, response field names, and frontend/backstage naming mismatches.
   - Entity/domain object: field type, length assumptions, enum/code normalization, transient fields, and persistence annotations.
   - Service layer: transformations, cross-service payload construction, fallback behavior, and null handling.
   - Mapper interface/XML: method signature, `@Param` names, `parameterType`, `resultMap`, dynamic SQL branches, selected column aliases, update/insert columns, and collection handling.
   - SQL/database: real table and column names, column lengths, constraints, indexes, not-null/default rules, and vendor-specific errors such as Oracle `ORA-12899`.
5. Check cross-service contracts.
   - When one service calls another, compare outbound parameter names and response fields against the receiver's expected contract.
   - Pay special attention to file and model contracts such as `fileName` versus `downloadName`, code versus display name fields, and numeric/string enum drift such as `1.0` versus `1`.
6. Verify before and after edits.
   - Before editing, reopen every file you will modify and the immediate caller/callee or mapper XML that depends on it.
   - After editing, reopen the changed files from disk and re-check the exact contract points fixed.
   - When available, run focused tests or a compile/lint command. If not available, explain the static verification performed.
7. Report the trace, not just the fix.
   - Name the concrete path: route -> controller -> service -> mapper -> XML/SQL -> table/column/constraint -> downstream service.
   - State the contract mismatch, the evidence, the change made or recommended, and remaining uncertainty.

## Search Hints

Use fast repository search first:

```powershell
rg -n "request-path|ControllerName|methodName|error-code|SQL fragment" .
rg -n "MapperName|resultMap|column_name|dtoField|jsonField" .
```

For Java/Spring/MyBatis projects, check these common patterns:

- `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PathVariable`, `@RequestParam`, `@RequestBody`
- DTO/VO classes, validation annotations, Jackson/FastJSON field annotations
- service implementations and Feign/HTTP client wrappers
- mapper interfaces and matching `*Mapper.xml`
- `resultMap`, `select`, `insert`, `update`, dynamic `<if>`, `<choose>`, `<foreach>`, and SQL aliases

## Output Shape

Prefer a concise structured answer:

```text
Trace:
route -> controller -> service -> mapper -> XML SQL -> table.column/constraint -> downstream contract

Finding:
The failing contract is ...

Evidence:
- file:line ...
- log/SQL clue ...

Change:
...

Verification:
...
```
