import { describe, it, expect } from "@jest/globals";

describe("App", () => {
  it("basic sanity check", () => {
    // simple smoke test so `yarn test` runs without extra test libs installed
    expect(true).toBe(true);
  });
});
