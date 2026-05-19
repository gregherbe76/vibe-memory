# Progress

Last updated: 2026-04-22

## In progress

- Checkout v2: switching from Stripe Checkout to Stripe Elements (started 2026-04-18). PR #142 open. Needs webhook handler updates for `payment_intent.succeeded` path.

## Next

1. Backfill `subscriptions.plan_id` for accounts created before 2026-03-01
2. Add Playwright coverage for the failed-payment retry flow
3. Migrate `lib/billing/` from CommonJS-style exports to named exports

## Completed (last 10)

- 2026-04-19 — Resend integration for receipt emails
- 2026-04-15 — Drizzle migration 0042: add `subscriptions.cancel_at_period_end`
- 2026-04-10 — Upgraded to Next.js 15
- 2026-04-04 — Clerk webhook for user.deleted now soft-deletes app rows
- 2026-03-28 — Switched from Vitest 1.x to 2.x

## Blocked

None.
