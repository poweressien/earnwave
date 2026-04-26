# 🚂 Deploying EarnWave to Railway

## Prerequisites
- GitHub account (free)
- Railway account (free) — sign up at railway.app with GitHub

---

## Step 1 — Push Code to GitHub

```bash
# In your earnwave folder (where manage.py is)
git init
git add .
git commit -m "EarnWave initial deploy"

# Create a new repo on github.com then:
git remote add origin https://github.com/YOUR_USERNAME/earnwave.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Create Railway Project

1. Go to **railway.app** → click **"Start a New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select your `earnwave` repository
4. Railway will detect Django and start building

---

## Step 3 — Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically sets `DATABASE_URL` — no action needed

---

## Step 4 — Set Environment Variables

Click your web service → **"Variables"** tab → Add these one by one:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Run `python generate_secret.py` locally to get one |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourapp.up.railway.app` (Railway gives you this URL) |
| `CSRF_TRUSTED_ORIGINS` | `https://yourapp.up.railway.app` |
| `PAYSTACK_PUBLIC_KEY` | `pk_test_your_key` (from paystack.com) |
| `PAYSTACK_SECRET_KEY` | `sk_test_your_key` (from paystack.com) |

> **ALLOWED_HOSTS**: Railway shows your app URL after first deploy.
> Come back and update this variable with the real URL.

---

## Step 5 — Deploy

Railway auto-deploys on every `git push`. Watch the build logs.

On first deploy it will automatically run:
- `python manage.py migrate`
- `python manage.py seed_data`
- `python manage.py seed_content`
- `python manage.py collectstatic`

---

## Step 6 — Your Site is Live! 🎉

Visit your Railway URL — it looks like:
`https://earnwave-production-xxxx.up.railway.app`

Admin panel: `/admin` → `admin@earnwave.ng` / `Admin@1234`

---

## Custom Domain (Optional)

1. Railway dashboard → your service → **"Settings"** → **"Domains"**
2. Add your domain (e.g. `earnwave.ng`)
3. Update your domain's DNS with Railway's CNAME
4. Add your domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` env vars

---

## Troubleshooting

**Build fails?**
- Check build logs in Railway dashboard
- Make sure all files are committed: `git status`

**"DisallowedHost" error?**
- Add your Railway URL to `ALLOWED_HOSTS` env variable

**Static files not loading?**
- Whitenoise handles this automatically — check `STATICFILES_STORAGE` in settings

**Database errors?**
- Make sure PostgreSQL plugin is added
- Check `DATABASE_URL` is set in your service variables
