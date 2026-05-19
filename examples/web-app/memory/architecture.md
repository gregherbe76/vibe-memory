# Architecture

Last updated: 2026-04-22
Current version: 0.7.3

## Stack

- TypeScript 5.4, React 19, Next.js 15 (App Router)
- Postgres 16 via Neon (serverless driver)
- Drizzle ORM for schema + queries
- Tailwind CSS 4, shadcn/ui components
- Auth: Clerk
- Payments: Stripe Checkout + webhook handler
- Hosted on Vercel; CI on GitHub Actions

## Components

- `app/` — Next.js routes; `(marketing)`, `(app)`, `(api)` route groups
- `app/api/stripe/webhook/route.ts` — Stripe event handler, idempotent on `event.id`
- `lib/db/` — Drizzle schema, migrations, query helpers
- `lib/billing/` — Stripe client wrapper, plan→price mapping
- `lib/auth/` — Clerk wrappers, `requireUser` server helper
- `components/ui/` — shadcn primitives (do not edit, regenerate via CLI)
- `components/app/` — product-specific components

## Data flow

1. Request hits a Next.js route. Middleware checks Clerk session.
2. Server component or server action calls helpers in `lib/`.
3. `lib/db/` issues queries via Drizzle → Neon Postgres.
4. Stripe webhooks land at `/api/stripe/webhook`, verify signature, mutate DB inside a transaction.
5. Mutations trigger `revalidatePath` for affected routes.

## External dependencies

- Neon Postgres (`DATABASE_URL`)
- Clerk (`CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`)
- Stripe (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`)
- Resend for transactional email (`RESEND_API_KEY`)

## Conventions

- Server actions live next to their route, suffixed `.actions.ts`.
- All DB writes go through `lib/db/`; no inline Drizzle in routes.
- Stripe webhook handlers must be idempotent — key off `event.id`.
- Tests: Vitest for units, Playwright for the checkout flow.
- No client components above the route segment unless necessary; default to server components.
