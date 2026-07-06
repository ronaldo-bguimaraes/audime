# Playwright Route Glob Pattern — Query String Matching

## Problem

Route patterns like `**/v1/extracoes` do NOT match URLs with query strings appended (e.g. `http://localhost:5173/v1/extracoes?limit=100`).

Playwright's `page.route()` matches glob patterns against the **full URL** (including protocol, host, path, and query string). The literal part of the pattern must match the end of the URL exactly.

## Fix

Use a trailing `*` (single-star, matches any characters except `/`) to match optional query strings:

```ts
// ❌ Does NOT match /v1/extracoes?limit=100
page.route("**/v1/extracoes", handler);

// ✅ Matches both /v1/extracoes and /v1/extracoes?limit=100
page.route("**/v1/extracoes*", handler);
```

## Why this happens

- `**` matches any characters including `/` (globstar)
- `*` matches any characters except `/` (single segment wildcard)
- Playwright globs are matched against the **full URL string**, not just the pathname
- A query string like `?limit=100` is appended to the path, so an exact literal match fails

## Contrast with `**/v1/auth/**`

The pattern `**/v1/auth/**` works for `/v1/auth/me` because:
- The trailing `**` matches the extra path segment `me`
- There is no query string in `/v1/auth/me`

## Lesson for fixtures

When mocking API endpoints that may receive query parameters, always add `*` at the end of the path pattern:

```ts
// For endpoints with potential query strings
page.route("**/v1/extracoes*", handler);    // ← note the trailing *
page.route("**/v1/notas*", handler);        // safer for query params

// For endpoints with sub-resources
page.route("**/v1/extracoes/*", handler);  // separate route for /{id}
```
