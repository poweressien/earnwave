# 🚂 EarnWave — Full Railway Deployment Guide
# Step by step, nothing skipped.

---

## WHAT YOU NEED BEFORE STARTING
- Your earnwave folder on your computer (where manage.py lives)
- A GitHub account → sign up free at github.com
- A Railway account → sign up free at railway.app
- Git installed on your computer

### Check if Git is installed:
Open PowerShell and type:
```
git --version
```
If you see something like `git version 2.43.0` → you're good.
If you get an error → download Git from: https://git-scm.com/download/win
Install it, then restart PowerShell.

---

## ═══════════════════════════════════════
## PART 1 — PUSH YOUR CODE TO GITHUB
## ═══════════════════════════════════════

### STEP 1 — Open your earnwave folder in PowerShell

```
cd C:\Users\power\Downloads\earnwave
```

Confirm you're in the right place:
```
dir manage.py
```
You should see manage.py listed. If not, navigate to the correct folder.

---

### STEP 2 — Generate your SECRET_KEY

Run this:
```
python generate_secret.py
```

You'll see output like:
```
Your SECRET_KEY:
django-insecure-abc123xyz789-this-is-just-an-example-abc123
```

**Copy that key and save it in Notepad.** You'll need it in Part 3.

---

### STEP 3 — Initialize Git in your project

```
git init
```

You'll see:
```
Initialized empty Git repository in C:/Users/power/Downloads/earnwave/.git/
```

---

### STEP 4 — Stage all files

```
git add .
```

No output is normal — it just stages everything silently.

---

### STEP 5 — Make your first commit

```
git commit -m "EarnWave first deploy"
```

You'll see a list of files being committed:
```
[main (root-commit) abc1234] EarnWave first deploy
 91 files changed, 3500 insertions(+)
 create mode 100644 manage.py
 create mode 100644 requirements.txt
 ...
```

---

### STEP 6 — Create a GitHub repository

1. Open your browser → go to **github.com**
2. Sign in to your account
3. Click the **"+"** button (top right corner) → **"New repository"**
4. Fill in:
   - Repository name: `earnwave`
   - Description: `Nigerian gamified rewards platform`
   - Set to **Public** (free hosting needs this)
   - Do NOT tick "Add README" or anything else
5. Click **"Create repository"**

GitHub will show you a page with setup commands. You'll see something like:
```
…or push an existing repository from the command line
git remote add origin https://github.com/YourUsername/earnwave.git
```

---

### STEP 7 — Connect your local code to GitHub

Copy the exact command GitHub shows you (it has your username in it):
```
git remote add origin https://github.com/YourUsername/earnwave.git
```

Then run:
```
git branch -M main
git push -u origin main
```

GitHub will ask for your username and password.
**Note:** GitHub no longer accepts passwords — use a Personal Access Token instead.

#### How to create a GitHub Personal Access Token:
1. GitHub → click your profile photo (top right) → **Settings**
2. Scroll all the way down → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. Click **"Generate new token (classic)"**
5. Give it a name like `earnwave-deploy`
6. Set expiry to **90 days**
7. Tick the **"repo"** checkbox
8. Click **"Generate token"**
9. **Copy the token immediately** (you can't see it again)

When git asks for password → paste your token instead.

After pushing you'll see:
```
Enumerating objects: 150, done.
Writing objects: 100% (150/150)
To https://github.com/YourUsername/earnwave.git
 * [new branch]      main -> main
```

✅ **Your code is now on GitHub!**

---

## ═══════════════════════════════════════
## PART 2 — SET UP RAILWAY
## ═══════════════════════════════════════

### STEP 8 — Sign up on Railway

1. Go to **railway.app**
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub
4. You're in! Railway dashboard opens.

---

### STEP 9 — Create a new project

1. Click **"New Project"** (big button in the middle)
2. Click **"Deploy from GitHub repo"**
3. If it says "No repos found" → click **"Configure GitHub App"** → give Railway access to your repos
4. You'll see your repositories listed → click **"earnwave"**
5. Railway starts building immediately — you'll see a progress log

While it builds, continue to the next step.

---

### STEP 10 — Add a PostgreSQL Database

Your app needs a database. Railway gives you one free.

1. In your Railway project, click **"+ New"** (top right of the project view)
2. Click **"Database"**
3. Click **"Add PostgreSQL"**
4. Railway creates the database and automatically connects it to your app
5. You'll see a new box appear in your project called **"Postgres"**

Railway automatically sets the `DATABASE_URL` variable — EarnWave is already configured to use it.

---

### STEP 11 — Set Environment Variables

This is the most important step. Click on your **web service box** (the earnwave one, not Postgres).

Then click the **"Variables"** tab.

Add each variable by clicking **"+ New Variable"**:

#### Variable 1 — SECRET_KEY
- Name: `SECRET_KEY`
- Value: paste the long key you generated in Step 2
- Example: `django-insecure-abc123xyz789-this-is-just-an-example-abc123`

#### Variable 2 — DEBUG
- Name: `DEBUG`
- Value: `False`

#### Variable 3 — ALLOWED_HOSTS
⚠️ First deploy first — you need the Railway URL for this.
Skip for now, we'll add it in Step 13.

#### Variable 4 — CSRF_TRUSTED_ORIGINS
Skip for now too — same reason.

#### Variable 5 — PAYSTACK_PUBLIC_KEY
- Name: `PAYSTACK_PUBLIC_KEY`
- Value: `pk_test_your_key_here`
(Get real keys from paystack.com after testing)

#### Variable 6 — PAYSTACK_SECRET_KEY
- Name: `PAYSTACK_SECRET_KEY`
- Value: `sk_test_your_key_here`

After adding SECRET_KEY and DEBUG, Railway will automatically redeploy.

---

### STEP 12 — Watch the First Deployment

Click **"Deployments"** tab on your service to watch the live build log.

You'll see Railway:
1. Installing Python
2. Running `pip install -r requirements.txt`
3. Running `python manage.py migrate`
4. Running `python manage.py collectstatic`
5. Starting gunicorn

A successful deploy ends with:
```
[INFO] Booting worker with pid: 12
[INFO] Worker is ready. Booting worker with pid: 13
```

If there's an error — scroll up in the logs and look for red text.

---

### STEP 13 — Get Your Live URL and Update Variables

Once deployed, click **"Settings"** tab on your service.

Under **"Domains"** you'll see your URL, something like:
```
earnwave-production-a1b2c3.up.railway.app
```

Now go back to **"Variables"** tab and add:

#### Variable 3 — ALLOWED_HOSTS
- Name: `ALLOWED_HOSTS`
- Value: `earnwave-production-a1b2c3.up.railway.app`
(use YOUR actual URL, not this example)

#### Variable 4 — CSRF_TRUSTED_ORIGINS
- Name: `CSRF_TRUSTED_ORIGINS`
- Value: `https://earnwave-production-a1b2c3.up.railway.app`
(note the `https://` at the start)

Railway will redeploy automatically.

---

### STEP 14 — Seed Your Production Database

Once the deploy is successful, click **"+ New"** → No, actually:

In your Railway service, click the three dots **"..."** → **"Railway Shell"** or look for a **"Shell"** or **"Console"** tab.

Type:
```
python setup_production.py
```

You'll see:
```
🌊 Setting up EarnWave production data...
✅ Admin created
✅ 6 quiz categories
✅ 3 quizzes with questions
✅ 3 surveys with questions
✅ 4 games
✅ 7 badges
✅ Setup complete!
```

This creates your admin account and loads all the content.

---

### STEP 15 — Visit Your Live Site! 🎉

Open your Railway URL in the browser:
```
https://earnwave-production-a1b2c3.up.railway.app
```

Your EarnWave site is live!

Admin panel:
```
https://earnwave-production-a1b2c3.up.railway.app/admin
Email:    admin@earnwave.ng
Password: Admin@1234
```

**⚠️ IMPORTANT: Change the admin password immediately!**
Admin panel → top right → Change Password

---

## ═══════════════════════════════════════
## PART 3 — AFTER YOU'RE LIVE
## ═══════════════════════════════════════

### How to Update Your Site Later

Every time you make a change locally, just push to GitHub:
```
git add .
git commit -m "describe what you changed"
git push
```

Railway auto-detects the push and redeploys. Takes about 2 minutes.

---

### How to Add a Custom Domain (e.g. earnwave.ng)

1. Railway service → **Settings** → **Domains** → **"Add Custom Domain"**
2. Type your domain: `earnwave.ng`
3. Railway shows you a CNAME record like:
   ```
   CNAME  earnwave.ng  →  abc123.railway.app
   ```
4. Log in to your domain registrar (where you bought the domain)
5. Find DNS settings → Add that CNAME record
6. Wait 10–30 minutes for DNS to propagate
7. Update your `ALLOWED_HOSTS` env variable to include `earnwave.ng`
8. Update `CSRF_TRUSTED_ORIGINS` to include `https://earnwave.ng`

---

### Railway Free Tier Limits

- **$5 credit/month** — enough for low traffic
- When credit runs out → app pauses (upgrade for $5/month)
- PostgreSQL database: free forever on Hobby plan
- No sleep/spin-down like other free hosts

---

## TROUBLESHOOTING

### "DisallowedHost" error on the site
→ Your URL is not in ALLOWED_HOSTS
→ Go to Variables → update ALLOWED_HOSTS with your exact Railway URL

### "CSRF verification failed" on login/signup
→ CSRF_TRUSTED_ORIGINS is missing or wrong
→ Make sure it starts with `https://` and matches your URL exactly

### Static files (CSS/images) not loading
→ Run `python manage.py collectstatic --no-input` in Railway shell
→ Or push an empty commit to trigger redeploy: `git commit --allow-empty -m "trigger redeploy" && git push`

### "Internal Server Error" (500)
→ Set `DEBUG=True` temporarily to see the error
→ Fix it, then set `DEBUG=False` again

### Build fails — "No module named X"
→ The package is missing from requirements.txt
→ Add it locally, test, then push again

---

## QUICK REFERENCE CHEATSHEET

| Task | Command |
|------|---------|
| Push update to live site | `git add . && git commit -m "update" && git push` |
| Generate new secret key | `python generate_secret.py` |
| Check project locally | `python manage.py check` |
| Run locally | `python manage.py runserver` |
| Add more content | `python manage.py seed_content` |
| Add demo users | `python manage.py seed_demo` |

