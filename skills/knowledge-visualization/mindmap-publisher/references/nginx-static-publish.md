# Nginx Static Publish Reference

Use this reference to map server paths to public URLs.

## Required Mapping

Publishing requires three deployment values:

```yaml
StaticRoot: /data/static/mindmaps
PublicBaseUrl: https://example.com
PathPrefix: /mindmaps
```

The generated URL is:

```text
https://example.com/mindmaps/{Slug}/index.html
```

The published files are:

```text
/data/static/mindmaps/{Slug}/index.html
/data/static/mindmaps/{Slug}/markmap-assets/...
```

## Nginx Example

```nginx
location /mindmaps/ {
    alias /data/static/mindmaps/;
    index index.html;
    try_files $uri $uri/ =404;
}
```

Important:

- `PathPrefix` is `/mindmaps`.
- `StaticRoot` is `/data/static/mindmaps`.
- The `alias` path should end with `/` when the `location` ends with `/`.
- Do not publish directly to the web root without a path prefix.

## URL Rules

Normalize inputs this way:

- `PublicBaseUrl`: no trailing slash.
- `PathPrefix`: starts with one slash, no trailing slash.
- `Slug`: one folder segment, no `/`, no `..`.

Examples:

```text
PublicBaseUrl = https://example.com
PathPrefix = /mindmaps
Slug = zero-trust
URL = https://example.com/mindmaps/zero-trust/index.html
```

```text
PublicBaseUrl = https://docs.example.com
PathPrefix = /static/mindmaps
Slug = report-2026
URL = https://docs.example.com/static/mindmaps/report-2026/index.html
```

## Security Notes

- Require a non-root path prefix to avoid accidental publication at domain root.
- Keep each mindmap in its own slug directory.
- Add cleanup or expiration at the application/deployment layer if previews are temporary.
- Add authentication, signed URLs, or unguessable slugs for private content.
