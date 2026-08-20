# Contributing to Simpaudio

Thanks for wanting to help. This project is small and community-driven — bug reports, fixes and ideas are all welcome.

## Ways to contribute

- **Report bugs** — open an issue using the bug report template. Include your version (Installer / Portable / source), Windows version, and the exact error text or a screenshot.
- **Suggest features** — use the feature request template and explain what problem it solves.
- **Fix bugs or add features** — follow the workflow below and open a pull request.

## Development setup

Simpaudio is a Python 3.11+ Tkinter app. The heavy engines (Piper, Kokoro, Whisper) run locally.

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

> Note: the project currently targets a Python 3.14 build environment. If dependencies fail to install, check the pinned versions in `requirements.txt` against your Python version.

## Verifying your changes

Before opening a PR, run the built-in self-test — it exercises Piper, Kokoro, voice blending and Whisper end to end:

```bat
python app.py --selftest --selftest-log selftest_results.log
```

The log should end with `[OK] overall: all checks passed`. Please mention the selftest result in your PR description.

## Building the release exe

```bat
build_exe.bat
```

This requires the global Python environment (not the `venv`) with all build dependencies installed, since the frozen app bundles the engine runtimes.

## Code style

- Follow the existing style of the codebase (PEP 8, no external formatting tooling is enforced).
- Do not add comments unless they explain something non-obvious.
- Keep changes focused; one logical change per PR.

## Pull request workflow

1. Fork the repository.
2. Create a branch: `git checkout -b fix/your-fix`.
3. Make your change and run the self-test.
4. Push and open a PR against `main`.
5. In the PR description, describe what changed and why, and paste the selftest result.

## Questions

Open a discussion or ask in the issue tracker. Please search existing issues first.
