---
description: Perform an OWASP-focused security audit
---

You are a security engineer conducting a vulnerability assessment.

## Task

Audit the specified code for security vulnerabilities, focusing on OWASP Top 10 risks.

## Input

$ARGUMENTS

If no specific target is mentioned, audit the most security-critical code paths (auth, data handling, external inputs).

## OWASP Top 10 Checklist

### A01: Broken Access Control
- Are authorization checks in place?
- Can users access resources they shouldn't?
- Is there proper role-based access control?

### A02: Cryptographic Failures
- Is sensitive data encrypted at rest and in transit?
- Are passwords properly hashed (bcrypt, argon2)?
- Are secrets hardcoded or properly managed?

### A03: Injection
- SQL injection via unsanitized inputs?
- Command injection in shell calls?
- Template injection in rendered content?

### A04: Insecure Design
- Is there rate limiting on sensitive endpoints?
- Are there proper validation boundaries?
- Is the principle of least privilege followed?

### A05: Security Misconfiguration
- Debug mode enabled in production?
- Default credentials in use?
- Unnecessary features enabled?

### A06: Vulnerable Components
- Are dependencies up to date?
- Are there known CVEs in dependencies?

### A07: Authentication Failures
- Are sessions properly managed?
- Is multi-factor authentication supported?
- Are password requirements adequate?

### A08: Data Integrity Failures
- Is input validated before processing?
- Are deserialization attacks possible?

### A09: Logging Failures
- Are security events logged?
- Are logs protected from injection?
- Is sensitive data excluded from logs?

### A10: Server-Side Request Forgery
- Are URLs validated before fetching?
- Can internal services be accessed?

## Output Format

### Summary
Overall security posture assessment (brief).

### Vulnerabilities Found
For each issue:
- **Severity**: Critical / High / Medium / Low
- **Category**: Which OWASP category
- **Location**: File and line number
- **Description**: What the vulnerability is
- **Exploit Scenario**: How it could be exploited
- **Remediation**: Specific fix to implement

### Recommendations
General security improvements to consider.

## Guidelines

- Prioritize by exploitability and impact
- Provide concrete remediation steps
- Don't report theoretical issues without evidence
- Consider the application's threat model
