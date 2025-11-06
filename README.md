# AdMaster AI Backend

🚀 **Production-grade Python backend for AdMaster AI**

AI-powered marketing automation platform API built with FastAPI, MongoDB, and Clerk authentication.

---

## 🏗️ Architecture

```
FastAPI (Python 3.11+)
├── MongoDB (Atlas) - Data storage
├── Clerk - Authentication
├── Beanie ODM - MongoDB object mapping
└── Async/Await - High performance
```

---

## 📁 Project Structure

```
admaster-backend/
├── app/
│   ├── core/              # Configuration, database, security
│   ├── models/            # MongoDB models (User, Business)
│   ├── schemas/           # Pydantic schemas (validation)
│   ├── services/          # Business logic
│   └── api/
│       └── v1/            # API endpoints
│           ├── businesses.py
│           ├── users.py
│           └── webhooks.py
├── tests/
├── requirements.txt
└── .env                   # Environment variables (create this!)
```

---

## 🚀 Quick Start

### 1. **Create `.env` file**

```bash
# Copy and fill in your values:
APP_NAME=AdMaster AI Backend
ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

HOST=0.0.0.0
PORT=8000

# MongoDB (IMPORTANT: Encode special chars in password!)
# @ = %40, # = %23, $ = %24
MONGODB_URL=mongodb+srv://devsvipul:AdmasterAi%402025@admasterai-cluster0.egdygrf.mongodb.net/?appName=AdMasterAI-Cluster0
MONGODB_DB_NAME=admaster

# Clerk (get from https://dashboard.clerk.com)
CLERK_SECRET_KEY=sk_test_your_key_here
CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. **Install Dependencies**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. **Run Server**

```bash
# Development (with auto-reload)
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. **Test It**

Open: http://localhost:8000/docs

You'll see interactive API documentation (Swagger UI)!

---

## 🔑 API Endpoints

### **Public Endpoints**

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /api/v1/webhooks/clerk` - Clerk webhook (syncs users)

### **Authenticated Endpoints** (Requires Clerk JWT token)

**Users:**

- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/me/profile` - Get user profile with stats

**Businesses:**

- `POST /api/v1/businesses` - Create business
- `GET /api/v1/businesses` - List all user's businesses
- `GET /api/v1/businesses/{id}` - Get specific business
- `PUT /api/v1/businesses/{id}` - Update business
- `DELETE /api/v1/businesses/{id}` - Delete business
- `GET /api/v1/businesses/check/has-business` - Check if user has any business

---

## 🔐 Authentication

This API uses **Clerk** for authentication.

### How it works:

1. Frontend gets JWT token from Clerk
2. Frontend sends token in `Authorization: Bearer <token>` header
3. Backend verifies token with Clerk
4. Backend fetches user from MongoDB using `clerk_id`

### Example API Call:

```javascript
// Frontend (Next.js)
const { getToken } = useAuth();
const token = await getToken();

const response = await fetch("http://localhost:8000/api/v1/businesses", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

---

## 🔄 Clerk Webhook Setup

To sync users from Clerk to MongoDB:

1. Go to: https://dashboard.clerk.com/last-active?path=webhooks
2. Click "Add Endpoint"
3. URL: `https://yourdomain.com/api/v1/webhooks/clerk`
4. Subscribe to events:
   - `user.created`
   - `user.updated`
   - `user.deleted`
5. Copy the "Signing Secret" to `.env` as `CLERK_WEBHOOK_SECRET`

---

## 💾 MongoDB Collections

### **users**

```python
{
  "clerk_id": "user_2abc123xyz",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "image_url": "https://...",
  "businesses": ["64a1b2c3...", "64a1b2c4..."],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### **businesses**

```python
{
  "user_id": "user_2abc123xyz",
  "name": "Corider",
  "website": "https://corider.in",
  "industry": "Technology",
  "size": "Small (1 - 10 employees)",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 📦 Deployment

### **Production Checklist:**

- [ ] Set `ENV=production` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` (min 32 chars)
- [ ] Restrict `ALLOWED_ORIGINS` to your actual frontend domain
- [ ] Set up MongoDB Atlas network restrictions
- [ ] Set up Clerk webhook with production URL
- [ ] Use process manager (PM2, systemd, or Docker)

### **Run with Gunicorn:**

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🐛 Troubleshooting

### MongoDB Connection Failed

- Check your connection string has encoded special characters
- Password has `@`? Change to `%40`
- Verify IP is whitelisted in MongoDB Atlas

### Clerk Token Invalid

- Ensure `CLERK_SECRET_KEY` is correct
- Check frontend is sending token in `Authorization` header
- Token format: `Bearer <token>`

### CORS Errors

- Add your frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart server after changing `.env`

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Beanie ODM](https://roman-right.github.io/beanie/)
- [Clerk API Reference](https://clerk.com/docs/reference/backend-api)
- [MongoDB Atlas](https://www.mongodb.com/docs/atlas/)

---

**Built with ❤️ by the AdMaster AI team**
