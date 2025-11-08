const { exec } = require("child_process");

module.exports = async () => {
  // Start the frontend dev server before Playwright tests
  const proc = exec("yarn start", { cwd: __dirname + "/../" });
  // Wait a few seconds for the server to start
  await new Promise((resolve) => setTimeout(resolve, 8000));
  return proc;
};
