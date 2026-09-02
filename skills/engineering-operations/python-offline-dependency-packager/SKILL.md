---
name: python-offline-dependency-packager
description: Download an exact Python package version for an explicitly supplied target Python minor-version line, including all transitive dependencies, and generate standalone PowerShell and POSIX-shell offline installers. Use when preparing a reproducible dependency bundle for an offline or restricted-network machine; do not use when the package version or target Python X.Y or X.Y.x value is missing.
---

# Python Offline Dependency Packager

Use `scripts/download_package.py` to resolve one pinned package, download its full dependency closure, and create a portable offline bundle.

## Workflow

1. Require the user to supply all three values: package name, exact package version, and target Python version in `X.Y` or `X.Y.x` form. Never infer the target Python version from the current interpreter. If either version is missing or ambiguous, ask for it and do not run the downloader. Normalize `X.Y.x` to the `X.Y` compatibility line.
2. From the repository root, run the downloader with the repository Python launcher:

   ```powershell
   .\scripts\run-python.ps1 .\skills\engineering-operations\python-offline-dependency-packager\scripts\download_package.py `
     --package requests --version 2.32.5 --python-version 3.11
   ```

   `--python-version 3.11.x` is equivalent and is normalized to `3.11` before pip runs.

3. Deliver the generated directory under `output/python-offline-dependency-packager/`. It contains:
   - `packages/`: the pinned package and every dependency selected by pip.
   - `requirements.txt`: the exact requested root requirement.
   - `bundle-manifest.json`: target metadata plus SHA-256 hashes for downloaded files.
   - `install.ps1`: one-click PowerShell installer.
   - `install.sh`: one-click POSIX-shell installer.
4. On the offline machine, extract or copy the complete directory, then run one installer:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```

   ```bash
   sh ./install.sh
   ```

5. Verify the package after installation with the target interpreter, using the import name supplied by the user when it differs from the distribution name.

## Target Compatibility

The target Python minor-version line is always required. The downloader defaults to CPython and derives its ABI tag from that version; for example, `3.11.x` becomes pip target `3.11` with ABI `cp311`. Pip then selects the newest available transitive dependency versions compatible with that Python line and the pinned root package. This does not download Python itself or resolve `3.11.x` to a concrete Python patch release. The current machine supplies the default platform unless `--platform` is provided.

For another platform, pass the target selector explicitly:

```powershell
.\scripts\run-python.ps1 .\skills\engineering-operations\python-offline-dependency-packager\scripts\download_package.py `
  --package cryptography --version 45.0.6 --python-version 3.12 `
  --platform win_amd64
```

Wheel-only mode is the default because it produces installation-ready bundles. Use `--allow-source` only when the offline machine has the required compilers and build tooling. Pip configuration and environment variables may be used for approved private indexes; never embed credentials in the bundle or command examples.

The downloader refuses to overwrite an existing output directory. Choose a new `--output` path or remove the old bundle only after confirming it is safe to do so.
