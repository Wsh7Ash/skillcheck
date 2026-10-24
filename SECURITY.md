# Security Policy

## Authorized use

`skillcheck` is a **defensive tool for systems you own or are explicitly authorized to
test**. Do not point it at third-party infrastructure without written permission;
unauthorized security testing violates computer-misuse laws in most jurisdictions.

`skillcheck` only reads the files you name; it never executes skill content, never resolves URLs, and makes no network requests. Review skill files before running them in an agent — they contain instructions an agent may act on.

## Reporting a vulnerability

If you find a vulnerability or unsafe default in `skillcheck` itself, please open a
private security advisory on the GitHub repository (or open an issue describing the
problem at a high level if you cannot use advisories). We will acknowledge within
72 hours and coordinate a fix before public disclosure.

## Secrets

`skillcheck` stores no credentials and requires none. Do not commit real tokens, cookies
or keys to the spec/example files in this repository; `.gitignore` excludes `.env`
and common key material.
