# E2E Tests with Playwright

## Running Tests Locally

### 1. Start the Frontend Dev Server
```bash
# In terminal 1
cd app/frontend
yarn start
```

Wait for the server to start (usually takes 10-15 seconds).

### 2. Run the Tests
```bash
# In terminal 2 (or same terminal after server is running)
cd app/frontend
yarn test:e2e
```

### Alternative: Run with UI Mode (Recommended for debugging)
```bash
yarn test:e2e:ui
```

### Run Specific Tests
```bash
# Run only homepage tests
yarn test:e2e playwright-tests/homepage.spec.js

# Run only auth tests  
yarn test:e2e playwright-tests/auth.spec.js
```

## Test Files

- `homepage.spec.js` - Tests homepage loads correctly
- `auth.spec.js` - Tests user registration, login, logout flow
- `login.spec.js` - Tests login form behavior
- `form.spec.js` - Tests contact form submission
- `navbar.spec.js` - Tests navigation for authenticated users
- `login-dashboard-ads.spec.js` - Tests dashboard and ads workflow
- `fullsite.spec.js` - Master diagnostic test

## Notes

- **Backend Required**: Most tests require the backend API to be running at `http://localhost:8000`
- **Frontend Required**: All tests require the frontend at `http://localhost:3000`
- **In CI**: The frontend server starts automatically
- **Locally**: You must start the frontend manually before running tests

## Troubleshooting

### Tests timeout waiting for elements
- Make sure both frontend and backend servers are running
- Check that ports 3000 and 8000 are available
- Try running tests with `--debug` flag: `yarn test:e2e:debug`

### Webserver timeout error
- The playwright config expects the server to be pre-started locally
- In CI, it will auto-start
- You can force auto-start locally by setting `CI=true` environment variable
