This folder archives a previously committed, generated HTML snapshot of the "Pressmaster Integrations" page.

Why archived here

- The snapshot was an auto-generated Next.js runtime HTML blob that does not belong in source control as an active source file.
- Keeping a copy in docs/ preserves the snapshot for reference without polluting the codebase root.

What to do

- If you need to regenerate the snapshot, run the build on the Next.js project and export the page snapshot to this folder.
- If the snapshot is large or contains secrets, remove it and rely on an external archive (S3, artifact registry) instead.

Note: This README intentionally does not include the snapshot HTML to avoid committing large binaries into git history.
