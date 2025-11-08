#!/bin/bash
# Bash script to run backend tests and coverage from project root
TEST_PATH="app/backend/tests/"
COV_PATH="app/backend"
echo "Running backend tests with coverage..."
python -m pytest --cov=$COV_PATH $TEST_PATH
