# Backend TODO (synchronized with chat)

Generated: 2025-10-16

This file mirrors the in-chat todo list and will be updated whenever tasks are changed during work sessions.

## Current tasks

- [x] Investigate TLS error
  - Locate MongoDB client creation and TLS/CA handling in backend code, confirm certifi use, and add tlsCAFile where needed.
- [x] Reorder env keys in `.env.example`
  - Alphabetize and place `ACCESS_TOKEN_EXPIRE_MINUTES` before `JWT_SECRET_KEY` to satisfy dotenv-linter.
- [~] Map placeholders to real values
  - Replace angle-bracket and ALL_CAPS placeholders with descriptive, lowercase placeholders and add generation notes (openssl, Fernet).
- [ ] Standardize placeholder style across templates
- [ ] Untrack any committed `.env` files
  - Identify tracked `.env` files, `git rm --cached` them and add `.gitignore` entries. Commit after confirmation.
- [~] Make `create_admin.py` prompt for password
  - Updated to support `--prompt`; prefer interactive prompt to avoid CLI passwords.
- [~] Add modal-on-click prompt for product tiles
  - Added `AuthPromptModal` and updated `App.js`/components to gate product actions; continue wrapping CTA buttons.
- [~] Scaffold Settings/Integrations UI + API
  - Plan: Add `backend/routes/integrations.py` (GET/PUT), frontend Settings page + Integrations component (admin-only).

## How I will keep this synced

1. I will update this file and commit every time the chat-managed todo list changes.
2. I will also update the chat-managed todo via the `manage_todo_list` tool so both are authoritative.
3. If you want this mirrored into Google Keep or a Google Doc, I can provide a one-click paste snippet or instructions for Zapier/Make to sync repo changes to a Keep note.

## Next actions you can request

- Ask me to create GitHub Issues from these items.
- Ask me to implement the Integrations endpoints and frontend UI now.
- Ask me to run `create_admin.py --prompt` locally (I can run it here if you confirm and provide safe envs).
