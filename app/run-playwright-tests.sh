#!/bin/bash
# Bash script to run Playwright E2E tests from project root
cd app/frontend
npx playwright test playwright-tests
cd ../..
