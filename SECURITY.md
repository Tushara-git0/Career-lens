# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please **do NOT open a public issue**.
Instead, email: tusharagoudu@gmail.com

We will respond within 48 hours and issue a patch as soon as possible.

---

## Environment Variables & Secrets

This project uses environment variables for all sensitive configuration.

**Never commit your `.env` file.** It is gitignored by default.

To set up locally:
```bash
cp .env.example .env
# Edit .env and fill in your real values
```

### Generating a Secure JWT Secret
```bash
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

---

## Dependencies

- Keep all dependencies up to date: `npm audit fix` and `pip install --upgrade -r requirements.txt`
- Review `npm audit` output before deploying to production.

---

## CORS

- The CareerLens AI FastAPI backend currently allows all origins (`*`) for local development.
- **Before production deployment**, restrict this to your actual frontend domain in `backend/main.py`.

## JWT Token Expiry

- JWT tokens are set to expire in **30 days**.
- Reduce this to `7d` or `1d` for production environments.
