Developer notes — enabling Git hooks

This repository includes a simple pre-commit hook under `.githooks/pre-commit` that prevents accidentally committing legacy brand tokens (for example, an old internal name).

To enable the hook locally:

1. From the repo root run:

   git config core.hooksPath .githooks

2. Make sure you have Python 3 installed and on your PATH. The hook calls `python3`; on Windows you may need to use a Python installer that adds `python`/`python3` to PATH.

3. The hook checks staged files. If it finds tokens, it blocks the commit and prints the offending files and lines.

If you manage hooks centrally (CI or developer setup) you can also run the checker directly:

python scripts/check_no_legacy_brand.py --staged
