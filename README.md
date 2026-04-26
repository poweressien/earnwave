# 🌊 EarnWave — Nigerian Gamified Rewards Platform

> **Earn Airtime. Play. Win. Repeat.**

EarnWave is a production-ready full-stack Django web application for a Nigerian gamified rewards platform where users earn airtime by completing surveys, playing quizzes, solving brain games, watching ads, and referring friends.

---

## ✨ Features

### 🎯 Core Earning Mechanisms
| Feature | Points Earned |
|---------|--------------|
| Signup Bonus | 50 pts |
| Complete Survey | 30–500 pts |
| Quiz (per correct answer) | 10–20 pts |
| Brain Games | 20–50 pts |
| Watch Ad | 10 pts (5x daily max) |
| Refer a Friend | 100 pts per referral |
| Daily Login Streak | 5–50 pts/day |

### 🏆 Gamification System
- **4 Levels**: Bronze → Silver → Gold → Platinum
- **Badge System**: 7 achievement badges (Common → Legendary)
- **Login Streaks**: Daily rewards for consecutive logins
- **Leaderboard**: Weekly and All-Time rankings

### 📱 Airtime Redemption
- MTN, Airtel, Glo, 9mobile support
- 100 points = ₦1 airtime
- Minimum redemption: 1,000 points (₦10)
- Admin or automated processing via Paystack

### 🔐 Security & Anti-Fraud
- Rate limiting middleware
- Referral fraud protection
- Device/IP abuse detection
- Account lockout system

---

## 🏗️ Project Structure

```
earnwave/
├── earnwave/              # Django project settings
│   ├── settings.py
│   └── urls.py
├── accounts/              # User auth, profiles, OTP
│   ├── models.py          # User, UserProfile, OTPCode
│   ├── views.py           # signup, login, profile
│   ├── forms.py           # All auth forms
│   └── admin.py           # User admin panel
├── dashboard/             # User dashboard
│   ├── views.py           # Stats, activity feed
│   └── urls.py
├── surveys/               # Survey system
│   ├── models.py          # Survey, Questions, Responses
│   ├── views.py           # Survey list, detail, submit
│   └── admin.py
├── quizzes/               # Quiz & trivia system
│   ├── models.py          # Quiz, Questions, Attempts, Leaderboard
│   ├── views.py           # List, play, submit, leaderboard
│   └── admin.py
├── games/                 # Brain games
│   ├── models.py          # Game, GameSession
│   └── views.py           # List, play, complete
├── rewards/               # Points & airtime
│   ├── models.py          # PointTransaction, Redemption, Badge, Notification
│   ├── views.py           # Dashboard, redeem, watch ad
│   └── admin.py           # Full redemption management
├── referrals/             # Referral system
│   ├── models.py          # ReferralRecord with fraud scoring
│   └── views.py           # Referral dashboard
├── core/                  # Landing pages, middleware
│   ├── middleware.py      # AntiAbuseMiddleware (rate limiting)
│   ├── context_processors.py
│   ├── views.py           # Landing, how-it-works, FAQ, etc.
│   └── management/commands/seed_data.py
├── templates/             # All HTML templates
│   ├── base.html          # Master template
│   ├── core/              # Landing, about, FAQ pages
│   ├── dashboard/         # Dashboard UI
│   ├── accounts/          # Auth pages
│   ├── surveys/           # Survey UI
│   ├── quizzes/           # Quiz play UI
│   ├── games/             # Game UI (memory match, etc.)
│   ├── rewards/           # Points & redemption UI
│   └── referrals/         # Referral dashboard
└── static/
    ├── css/earnwave.css   # Complete design system
    └── js/earnwave.js     # Utilities & interactions
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourname/earnwave.git
cd earnwave

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
SECRET_KEY=your-very-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Paystack (get from paystack.com)
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# Email (Gmail example)
EMAIL_HOST_USER=yourapp@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# PostgreSQL (optional, SQLite used by default)
# USE_POSTGRES=True
# DB_NAME=earnwave
# DB_USER=postgres
# DB_PASSWORD=yourpassword
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py seed_data        # Loads sample surveys, quizzes, games & admin
```

### 4. Run
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**
Admin: **http://localhost:8000/admin** → `admin@earnwave.ng` / `Admin@1234`

---

## 🗄️ Database Models

### accounts.User (Custom)
- UUID primary key
- Email-based authentication
- Unique referral code (auto-generated)
- Fraud tracking: `login_attempts`, `is_locked`, `ip_address`

### accounts.UserProfile
- Gamification: `login_streak`, `longest_streak`, `total_points_earned`
- Activity: `surveys_completed`, `quizzes_completed`, `games_completed`
- Ad limits: `ads_watched_today`, `ads_watched_date`
- Preferences: `dark_mode`, `email_notifications`, `preferred_network`

### rewards.PointTransaction
- Full audit trail of all point credits/debits
- Sources: survey, quiz, game, ad_watch, referral, daily_login, redemption, admin
- Reference IDs for traceability

### rewards.AirtimeRedemption
- Status flow: pending → processing → completed / failed
- Network & phone number tracking
- Paystack reference integration

### rewards.Badge + UserBadge
- 4 rarity levels: Common, Rare, Epic, Legendary
- Condition-based auto-award system

### surveys.Survey + Questions + Responses
- Multi-type questions: multiple_choice, text, rating, boolean
- Eligibility filters: age, gender, state
- Sponsor support with logo

### quizzes.Quiz + Questions + Attempts
- Timed quiz system (per-question timers)
- Per-question correct answer tracking
- Score percentage calculation

### referrals.ReferralRecord
- Full referral chain tracking
- Fraud score field
- Automatic bonus distribution via `qualify_and_reward()`

---

## 🎨 Design System

**Color Palette**: Black (#0A0A0F) + White + Blue (#2563EB)
**Typography**: Syne (display) + DM Sans (body)
**Theme**: Dark by default, light mode toggle
**Components**: Cards, stat tiles, quiz arena, progress bars, leaderboards, toasts

---

## 💰 Monetization Architecture

- **Sponsored Surveys**: Brand surveys with `is_sponsored=True` + sponsor branding
- **Ad Watch**: Daily rewarded ad system (ready for AdMob/Google integration)
- **Offer Wall**: Architecture ready in rewards app
- **Paystack**: Integrated for airtime disbursement processing

---

## 🔧 Production Deployment

### Install for Production
```bash
pip install gunicorn psycopg2-binary
```

### Gunicorn
```bash
gunicorn earnwave.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Environment
```env
DEBUG=False
USE_POSTGRES=True
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=<strong-random-key>
```

### Nginx Config
```nginx
server {
    listen 80;
    server_name earnwave.ng;

    location /static/ { alias /path/to/earnwave/staticfiles/; }
    location /media/  { alias /path/to/earnwave/media/; }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📦 Requirements

```
Django>=4.2
djangorestframework
psycopg2-binary
Pillow
python-decouple
django-crispy-forms
crispy-bootstrap5
whitenoise
gunicorn
requests
qrcode
```

---

## 🔮 Roadmap

- [ ] Paystack automatic airtime disbursement
- [ ] SMS OTP via Termii/Infobip
- [ ] Push notifications (Firebase FCM)
- [ ] PWA manifest for installable web app
- [ ] React Native mobile app
- [ ] Advanced leaderboard with real-time updates
- [ ] Offer wall integration (CPAlead/AdGate)
- [ ] Analytics dashboard for admins
- [ ] Multi-language support (Hausa, Yoruba, Igbo)
- [ ] Spin wheel bonus game

---

## 🇳🇬 Built for Nigeria

- Nigerian network providers (MTN, Airtel, Glo, 9mobile)
- Africa/Lagos timezone
- Naira (₦) currency throughout
- JAMB-style quiz category
- Nigerian state fields for targeting

---

*EarnWave — Making the internet pay you back.*
#   e a r n w a v e  
 