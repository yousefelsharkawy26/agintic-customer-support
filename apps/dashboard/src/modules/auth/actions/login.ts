"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SignJWT } from "jose";

export async function login(prevState: { error: string } | null, formData: FormData) {
  const email = formData.get("email");
  const password = formData.get("password");

  // TODO: Phase 7 (User & Role Management) will replace this with an actual API call
  // to the FastAPI backend for human user authentication.
  if (email === "admin@example.com" && password === "password") {
    // Generate a valid JWT for FastAPI
    const secret = new TextEncoder().encode(
      process.env.JWT_SECRET || "tJB7su2wDmHxbBISiSzDy5aa13UzomZEgqG4PuMynF7"
    );

    // We use default tenant "default"
    const accessToken = await new SignJWT({
      tenant_id: "default",
      tenant_name: "Default Tenant",
      tenant_slug: "default",
      plan: "gpt-4o",
      auth_method: "password",
    })
      .setProtectedHeader({ alg: "HS256" })
      .setIssuedAt()
      .setExpirationTime("24h")
      .sign(secret);

    const dummyRefreshToken = "mock_refresh_token_67890";

    const cookieStore = await cookies();

    // Set Secure, HttpOnly, SameSite=Lax cookies
    cookieStore.set("access_token", accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 24 * 60 * 60, // 24 hours
      path: "/",
    });

    cookieStore.set("refresh_token", dummyRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 7 * 24 * 60 * 60, // 7 days
      path: "/",
    });

    redirect("/");
  } else {
    return { error: "Invalid credentials. Use admin@example.com / password" };
  }
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
  redirect("/login");
}
