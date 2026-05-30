import { describe, it, expect } from "vitest"
import { prisma } from "../src/lib/prisma"

describe("database", () => {
  it("should connect and query users table", async () => {
    const users = await prisma.user.findMany()
    expect(Array.isArray(users)).toBe(true)
  })

  it("should have User model fields", async () => {
    const user = await prisma.user.findFirst()
    if (user) {
      expect(user).toHaveProperty("id")
      expect(user).toHaveProperty("email")
      expect(user).toHaveProperty("googleId")
    }
  })
})
