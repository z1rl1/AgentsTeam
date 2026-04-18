---
name: auth-patterns
description: Authentication and authorization patterns including JWT flows, session management, middleware guards, RBAC, password hashing, and CSRF protection. Auto-loads when working with auth code, login, tokens, or permissions.
user-invocable: false
---

# Authentication & Authorization Patterns

Apply these patterns when implementing auth-related features.

## JWT Token Flow

### Access + Refresh Token Pattern
```
1. User logs in with credentials
2. Server validates credentials
3. Server returns:
   - Access token (short-lived: 15 min)
   - Refresh token (long-lived: 7 days, stored in httpOnly cookie)
4. Client sends access token in Authorization header
5. When access token expires, client uses refresh token to get a new pair
6. Refresh token rotation: issue new refresh token on each refresh (invalidate old one)
```

### Token Structure
```typescript
// Access token payload (keep small — sent with every request)
interface AccessTokenPayload {
  sub: string;      // user ID
  role: string;     // user role
  iat: number;      // issued at
  exp: number;      // expiration
}

// Sign with RS256 or HS256
const token = jwt.sign(payload, secret, { expiresIn: "15m" });
```

### Token Validation
```typescript
function verifyToken(token: string): TokenPayload {
  try {
    return jwt.verify(token, secret, {
      algorithms: ["HS256"], // explicitly specify allowed algorithms
    });
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      throw new AppError(401, "Token expired", "TOKEN_EXPIRED");
    }
    throw new AppError(401, "Invalid token", "INVALID_TOKEN");
  }
}
```

## Auth Middleware

```typescript
// Authentication — verify identity
const authenticate = asyncHandler(async (req, res, next) => {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    throw new AppError(401, "Missing token", "UNAUTHORIZED");
  }
  const token = header.slice(7);
  req.user = verifyToken(token);
  next();
});

// Authorization — verify permissions
const authorize = (...allowedRoles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!allowedRoles.includes(req.user.role)) {
      throw new AppError(403, "Insufficient permissions", "FORBIDDEN");
    }
    next();
  };
};

// Usage
router.get("/admin/users", authenticate, authorize("admin"), getUsers);
router.get("/profile", authenticate, getProfile);
```

## Password Handling

```typescript
import bcrypt from "bcrypt";

const SALT_ROUNDS = 12;

async function hashPassword(plaintext: string): Promise<string> {
  return bcrypt.hash(plaintext, SALT_ROUNDS);
}

async function verifyPassword(plaintext: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plaintext, hash);
}
```

**Rules:**
- Never store plaintext passwords
- Use bcrypt with cost factor >= 12
- Never log passwords (even hashed ones)
- Enforce minimum password complexity at the API boundary

## Session Management

### Secure Cookie Configuration
```typescript
res.cookie("refreshToken", token, {
  httpOnly: true,     // not accessible via JavaScript
  secure: true,       // HTTPS only
  sameSite: "strict", // CSRF protection
  path: "/api/auth",  // only sent to auth endpoints
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
});
```

## Role-Based Access Control (RBAC)

```typescript
// Define permissions per role
const PERMISSIONS = {
  admin: ["users:read", "users:write", "users:delete", "posts:*"],
  editor: ["posts:read", "posts:write", "posts:delete"],
  user: ["posts:read", "posts:write:own"],
} as const;

// Check specific permission
function hasPermission(role: string, permission: string): boolean {
  const rolePerms = PERMISSIONS[role] || [];
  return rolePerms.some(p =>
    p === permission || p === "*" || p.endsWith(":*") && permission.startsWith(p.slice(0, -1))
  );
}

// Middleware
const requirePermission = (permission: string) => (req, res, next) => {
  if (!hasPermission(req.user.role, permission)) {
    throw new AppError(403, "Forbidden", "INSUFFICIENT_PERMISSIONS");
  }
  next();
};
```

## CSRF Protection

For cookie-based auth (not needed for Bearer token auth):

```typescript
// Double-submit cookie pattern
// 1. Server sets a CSRF token cookie (readable by JS)
// 2. Client sends the token in a custom header
// 3. Server verifies cookie value matches header value
app.use(csrf({ cookie: true }));
```

## Security Headers

```typescript
app.use(helmet()); // sets secure HTTP headers

// Or manually:
app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  next();
});
```

## Anti-Patterns to Avoid

- Do NOT store JWTs in localStorage (XSS vulnerable) — use httpOnly cookies for refresh tokens
- Do NOT use symmetric algorithms without key rotation
- Do NOT include sensitive data in JWT payload (it's base64, not encrypted)
- Do NOT rely solely on client-side auth checks — always verify server-side
- Do NOT use a blocklist for authorization — use an allowlist (deny by default)
- Do NOT implement your own crypto — use established libraries (bcrypt, jose, etc.)
