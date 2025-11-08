#!/bin/bash
# Bash script to run frontend Jest tests and coverage from project root
cd app/frontend
yarn test --coverage --watchAll=false
cd ../..
