import { expect, test } from "@playwright/test";

test("home and library are reachable", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(String(err)));
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Start an investigation" })).toBeVisible();
  await page.getByRole("link", { name: "Explore examples" }).click();
  await expect(page.getByText("A progression of educational models")).toBeVisible();
  expect(errors).toEqual([]);
});
