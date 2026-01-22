# JWT Authentication

## Why

Users currently share a single demo account. We need individual accounts to track usage per user for billing and to enable personal settings.

## What

Users can register, log in, and refresh tokens. JWT-based auth with 1hr access tokens and 7d refresh tokens. Protected routes return 401 without valid token.

- POST /auth/register — create account, return tokens
- POST /auth/login — validate credentials, return tokens
- POST /auth/refresh — exchange refresh token for new access token
- GET /auth/me — return current user (protected)

## Constraints

### Must
- Use existing Express app structure in `src/server.ts`
- Use jsonwebtoken library (already in package.json)
- Store users in existing Postgres via Prisma
- Follow error handling pattern in `src/lib/errors.ts`

### Must Not
- Add new dependencies
- Modify existing user-facing routes
- Store tokens in database (stateless JWT)

### Out of Scope
- Password reset flow
- Email verification
- OAuth / social login

## Current State

- Server: Express in `src/server.ts`
- Routes: `src/routes/index.ts` exports router, individual routes in `src/routes/*.ts`
- DB: Prisma with schema in `prisma/schema.prisma`
- Errors: Pattern in `src/lib/errors.ts` (throw AppError, caught by error middleware)
- Auth: None yet

## Tasks

### T1: Add User model
**What:** Add User model to Prisma schema with id, email, passwordHash, createdAt. Run migration.
**Files:** `prisma/schema.prisma`
**Tests:** None
**Verify:** `npx prisma migrate dev` succeeds, User table exists

### T2: Create auth utilities
**What:** Create JWT sign/verify functions. signAccessToken (1hr), signRefreshToken (7d), verifyToken.
**Files:** `src/lib/jwt.ts`, `src/lib/jwt.test.ts`
**Tests:** Test sign and verify for valid tokens, expired tokens, invalid tokens
**Verify:** `npm test` passes

### T3: Create register endpoint
**What:** POST /auth/register accepts email/password, hashes password, creates user, returns tokens.
**Files:** `src/routes/auth.ts` (create), `src/routes/index.ts` (add auth routes)
**Tests:** `src/routes/auth.test.ts` — successful registration, duplicate email, invalid input
**Verify:** `npm test` passes, `curl` returns 201 with tokens

### T4: Create login endpoint
**What:** POST /auth/login accepts email/password, validates credentials, returns tokens.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — successful login, wrong password, nonexistent user
**Verify:** `npm test` passes, `curl` returns 200 with tokens or 401

### T5: Create refresh endpoint
**What:** POST /auth/refresh accepts refresh token, returns new access token.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — valid refresh, expired refresh, invalid refresh
**Verify:** `npm test` passes

### T6: Create auth middleware
**What:** Middleware that validates access token from Authorization header, attaches user to request.
**Files:** `src/middleware/auth.ts` (create), `src/types/index.ts` (extend Request type)
**Tests:** `src/middleware/auth.test.ts` — valid token, missing token, expired token, malformed token
**Verify:** `npm test` passes

### T7: Protect test route
**What:** Add GET /auth/me that requires auth and returns current user.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — with valid token returns user, without token returns 401
**Verify:** Full flow works: register → login → access /me with token
