import { prisma } from "../prisma/prisma";

import type { FastifyInstance } from "fastify";

import fp from "fastify-plugin";
import jwt from "@fastify/jwt";

import oauth2, { type OAuth2Namespace } from "@fastify/oauth2";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://localhost:5173";

async function authPlugin(app: FastifyInstance) {
  if (!process.env.JWT_SECRET) {
    throw new Error("JWT_SECRET env var is required");
  }

  await app.register(jwt, { secret: process.env.JWT_SECRET });

  if (!process.env.GOOGLE_CLIENT_ID || !process.env.GOOGLE_CLIENT_SECRET) {
    throw new Error(
      "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars are required",
    );
  }

  await app.register(oauth2, {
    name: "google",
    scope: ["openid", "profile", "email"],
    credentials: {
      client: {
        id: process.env.GOOGLE_CLIENT_ID,
        secret: process.env.GOOGLE_CLIENT_SECRET,
      },
      auth: oauth2.GOOGLE_CONFIGURATION,
    },
    startRedirectPath: "/auth/google",
    callbackUri: `${process.env.API_URL ?? "http://localhost:3333"}/auth/google/callback`,
  });

  app.decorate("authenticate", async (req, reply) => {
    try {
      await req.jwtVerify();
    } catch {
      reply.status(401).send({ error: "Unauthorized" });
    }
  });

  app.get("/auth/google/callback", async (req, reply) => {
    const { token: accessToken } =
      await app.google.getAccessTokenFromAuthorizationCodeFlow(req);

    const userInfo: {
      id: string;
      email: string;
      name: string;
      picture: string;
    } = await fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
      headers: { Authorization: `Bearer ${accessToken.access_token}` },
    }).then((r) => r.json());

    const user = await prisma.user.upsert({
      where: { googleId: userInfo.id },
      update: {
        name: userInfo.name,
        email: userInfo.email,
        avatar: userInfo.picture,
      },
      create: {
        googleId: userInfo.id,
        name: userInfo.name,
        email: userInfo.email,
        avatar: userInfo.picture,
      },
    });

    const sessionToken = await reply.jwtSign({ sub: user.id });

    return reply.redirect(
      `${FRONTEND_URL}/auth/callback?token=${sessionToken}`,
    );
  });

  app.get("/auth/me", { preHandler: [app.authenticate] }, async (req) => {
    const { sub } = await req.jwtVerify<{ sub: string }>();
    const user = await prisma.user.findUniqueOrThrow({
      where: { id: sub },
    });
    return { user };
  });
}

declare module "fastify" {
  interface FastifyInstance {
    authenticate: (
      request: import("fastify").FastifyRequest,
      reply: import("fastify").FastifyReply,
    ) => Promise<void>;
    google: OAuth2Namespace;
  }
}

export default fp(authPlugin, { name: "auth" });
