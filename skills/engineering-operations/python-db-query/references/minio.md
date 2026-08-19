# MinIO Through `mc`

Use the official MinIO Client (`mc`) for MinIO and other S3-compatible object stores. The wrapper is read-only with one local-output exception: `download` writes a named local file and refuses to overwrite it unless `--overwrite` is explicit.

The wrapper supplies a temporary `MC_HOST_skillsmanager` environment variable to the child process. It does not run `mc alias set`, modify `~/.mc/config.json`, or put access/secret keys in command-line arguments.

## Install `mc`

Do not download or install software without user approval. A user may instead supply an existing binary through `mc_path`.

### Windows x64

Download the official binary to the ignored dependency directory:

```powershell
Invoke-WebRequest https://dl.min.io/client/mc/release/windows-amd64/mc.exe -OutFile .\dependencies\mc.exe
.\dependencies\mc.exe --version
```

The wrapper searches `dependencies/mc.exe` and then `PATH`. A custom path can be set in config.

### Linux

For x64:

```bash
curl -fL https://dl.min.io/client/mc/release/linux-amd64/mc -o ./dependencies/mc
chmod +x ./dependencies/mc
./dependencies/mc --version
```

For ARM64, replace `linux-amd64` with `linux-arm64`. The wrapper searches `dependencies/mc` and then `PATH`.

## Config

Prefer environment-variable references so credentials are not stored in JSON:

```json
{
  "type": "minio",
  "endpoint": "https://minio.example.com",
  "access_key_env": "MINIO_ACCESS_KEY",
  "secret_key_env": "MINIO_SECRET_KEY",
  "mc_path": "dependencies/mc.exe"
}
```

`mc_path` is optional and resolves relative to the config file. Omit it when the binary is in the skill `dependencies/` directory or on `PATH`. On Linux a local value is normally `dependencies/mc`.

Optional fields:

- `session_token_env`: environment variable holding an STS session token.
- `anonymous`: use anonymous access; cannot be combined with credentials.
- `insecure`: disable TLS certificate verification. Use only when the user explicitly accepts that risk.
- Literal `access_key`, `secret_key`, and `session_token` are supported for compatibility but environment variables are preferred.

Initialize the config on Windows without writing credentials:

```powershell
..\..\..\scripts\run-python.ps1 .\scripts\init_config.py `
  --type minio `
  --endpoint https://minio.example.com `
  --access-key-env MINIO_ACCESS_KEY `
  --secret-key-env MINIO_SECRET_KEY `
  --mc-path .\dependencies\mc.exe
```

Linux equivalent:

```bash
python3 ./scripts/init_config.py \
  --type minio \
  --endpoint https://minio.example.com \
  --access-key-env MINIO_ACCESS_KEY \
  --secret-key-env MINIO_SECRET_KEY \
  --mc-path ./dependencies/mc
```

## Commands

Windows examples use the repository launcher:

```powershell
..\..\..\scripts\run-python.ps1 .\scripts\minio_mc.py --config .\config.json test-connection
..\..\..\scripts\run-python.ps1 .\scripts\minio_mc.py --config .\config.json list-buckets
..\..\..\scripts\run-python.ps1 .\scripts\minio_mc.py --config .\config.json list-objects assets --prefix images/ --recursive
..\..\..\scripts\run-python.ps1 .\scripts\minio_mc.py --config .\config.json stat assets images/logo.png
..\..\..\scripts\run-python.ps1 .\scripts\minio_mc.py --config .\config.json download assets images/logo.png .\outputs\logo.png
```

On Linux, replace the launcher prefix with `python3`:

```bash
python3 ./scripts/minio_mc.py --config ./config.json list-buckets
python3 ./scripts/minio_mc.py --config ./config.json list-objects assets --prefix images/ --recursive
```

All remote operation output is JSON Lines from `mc`. The wrapper adds `--json`, `--no-color`, `--quiet`, and `--disable-pager` for deterministic non-interactive use.

This wrapper intentionally does not expose upload, delete, mirroring, policy, or admin commands. Run mutating `mc` commands only as a separately authorized workflow.

Official references:

- [MinIO Client Quickstart and platform binaries](https://github.com/minio/mc/blob/master/README.md)
- [MinIO Client environment settings and `MC_HOST_<ALIAS>`](https://docs.min.io/aistor/reference/cli/aistor-client-settings/)
