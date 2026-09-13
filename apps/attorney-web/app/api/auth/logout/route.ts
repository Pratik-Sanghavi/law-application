export const dynamic = "force-dynamic";

import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const publicBaseUrl = process.env.APP_BASE_URL ?? new URL(req.url).origin;
  const issuer = process.env.OIDC_ISSUER_URL;
  const destination = issuer
    ? new URL(`${issuer}/protocol/openid-connect/logout`)
    : new URL("/", publicBaseUrl);

  if (issuer) {
    destination.searchParams.set(
      "client_id",
      process.env.OIDC_CLIENT_ID ?? "attorney-web",
    );
    destination.searchParams.set(
      "post_logout_redirect_uri",
      `${publicBaseUrl}/`,
    );
  }

  const response = NextResponse.redirect(destination, 303);
  response.cookies.delete("access_token");
  response.cookies.delete("oidc_state");
  response.cookies.delete("pkce_verifier");
  return response;
}
