---
name: api-design
description: REST API design conventions including resource naming, HTTP methods, response formats, pagination, error responses, and versioning. Auto-loads when designing or implementing API endpoints.
user-invocable: false
---

# REST API Design Conventions

Apply these conventions when designing or implementing API endpoints.

## Resource Naming

- Use plural nouns: `/users`, `/posts`, `/comments`
- Use kebab-case for multi-word resources: `/user-profiles`
- Nest for relationships (max 2 levels): `/users/:id/posts`
- Use query params for filtering, not URL segments: `/posts?author=123`

## HTTP Methods

| Method | Purpose | Idempotent | Response Code |
|--------|---------|------------|---------------|
| GET | Read resource(s) | Yes | 200 |
| POST | Create resource | No | 201 |
| PUT | Full replace | Yes | 200 |
| PATCH | Partial update | Yes | 200 |
| DELETE | Remove resource | Yes | 204 |

## Response Envelope

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "requestId": "req_abc123"
  }
}
```

### List Response
```json
{
  "data": [ ... ],
  "meta": {
    "total": 42,
    "page": 1,
    "pageSize": 20,
    "hasMore": true
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Status Codes

### Success
- `200 OK` — Successful read/update
- `201 Created` — Successful creation (include `Location` header)
- `204 No Content` — Successful deletion

### Client Errors
- `400 Bad Request` — Validation error, malformed request
- `401 Unauthorized` — Missing or invalid authentication
- `403 Forbidden` — Authenticated but insufficient permissions
- `404 Not Found` — Resource does not exist
- `409 Conflict` — Duplicate or state conflict
- `422 Unprocessable Entity` — Semantically invalid (valid JSON but bad data)
- `429 Too Many Requests` — Rate limit exceeded

### Server Errors
- `500 Internal Server Error` — Unexpected server error
- `503 Service Unavailable` — Temporary outage

## Pagination

Use cursor-based pagination for large datasets:

```
GET /posts?cursor=eyJpZCI6MTAwfQ&limit=20
```

Response includes:
```json
{
  "data": [...],
  "meta": {
    "nextCursor": "eyJpZCI6MTIwfQ",
    "hasMore": true
  }
}
```

For simple cases, offset pagination is acceptable:
```
GET /posts?page=2&pageSize=20
```

## Filtering & Sorting

```
GET /posts?status=published&author=123&sort=-createdAt&fields=id,title
```

- Prefix with `-` for descending sort
- Use `fields` parameter for sparse fieldsets
- Use consistent parameter names across all endpoints

## Request Validation

- Validate all input at the API boundary
- Return `400` with specific field-level errors
- Reject unknown fields (strict mode)
- Apply sensible defaults for optional parameters
- Limit `pageSize` to prevent abuse (e.g., max 100)

## Anti-Patterns to Avoid

- Do NOT use verbs in URLs (`/getUser`) — use HTTP methods instead
- Do NOT return `200` for errors — use appropriate error status codes
- Do NOT expose internal IDs or database structure in error messages
- Do NOT nest resources more than 2 levels deep
- Do NOT use `PUT` for partial updates — use `PATCH`
- Do NOT return different response shapes for the same endpoint based on conditions
