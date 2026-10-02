# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly. Do NOT create public GitHub issues for security vulnerabilities.

## Security Measures

### API Key Management

- Exchange API keys are stored in environment variables
- Never commit API keys to version control
- Use AWS Secrets Manager in production
- Never log API keys, secrets, or tokens

### Authentication

- All API endpoints require authentication
- JWT tokens for session management
- Role-based access control

### Input Validation

- All API inputs are validated
- SQL injection prevention via ORM
- XSS prevention via proper escaping

### Network Security

- HTTPS in production
- Rate limiting on API endpoints
- CORS configuration

### Live Trading Safety

- Live trading is disabled by default
- Requires explicit configuration
- Requires risk limits to be set
- No withdrawal permissions allowed
- Global kill switch available

## Best Practices

1. Never share API keys
2. Use separate keys for development and production
3. Rotate API keys regularly
4. Monitor exchange API usage
5. Enable IP whitelisting where supported
6. Use strong, unique passwords
7. Enable 2FA on exchange accounts

## Incident Response

1. Activate kill switch immediately
2. Revoke compromised API keys
3. Review audit logs
4. Notify affected users
5. Document the incident
