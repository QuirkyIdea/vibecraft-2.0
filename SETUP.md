# VibeCraft 2.0 Setup Guide

Complete setup instructions for running the Inventix AI platform locally.

## 📋 Prerequisites

- **Python 3.13** or higher
- **Node.js 18+** and npm
- **Git**
- **Google Gemini API Key** (free tier available at https://ai.google.dev/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/QuirkyIdea/vibecraft-2.0.git
cd vibecraft-2.0
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./data/app.db
SECRET_KEY=your-secret-key-here
```

To get your Gemini API key:
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Copy your API key and paste it in the `.env` file

#### Start Backend Server

```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API documentation at: **http://localhost:8000/docs**

### 3. Frontend Setup

Open a **new terminal** and navigate to the frontend directory:

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Configure Frontend Environment

The frontend automatically connects to `http://localhost:8000` for the backend API.

If you need to change this, create a `.env.local` file:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## 🎯 Project Structure

```
vibecraft-2.0/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── core/           # Schemas & config
│   │   └── main.py         # FastAPI app entry
│   ├── data/               # SQLite database & JSON files
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend config
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   └── context/       # State management
│   ├── package.json       # Node dependencies
│   └── .env.local         # Frontend config
│
└── docs/                   # Documentation
```

## ✨ Key Features

1. **Draft Refinement** - AI-powered academic text refinement
2. **Conference Recommendations** - Smart conference matching
3. **Patent Risk Analysis** - IP conflict detection
4. **Research Assistant** - Literature analysis
5. **Project Management** - Research project tracking

## 🔧 Troubleshooting

### Backend Issues

**Problem: ModuleNotFoundError**
```bash
# Solution: Reinstall dependencies
cd backend
pip install -r requirements.txt
```

**Problem: Gemini API quota exceeded**
- Free tier has 20 requests/day limit
- The system automatically falls back to rule-based refinement
- Or upgrade to paid tier at https://ai.google.dev/pricing

**Problem: Port 8000 already in use**
```bash
# Solution: Use a different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
# Update frontend API_URL accordingly
```

### Frontend Issues

**Problem: npm install fails**
```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem: API connection refused**
- Ensure backend is running on port 8000
- Check backend terminal for errors
- Verify CORS settings in backend

**Problem: Port 3000 already in use**
```bash
# Solution: Next.js will prompt to use port 3001 automatically
# Or manually specify port:
npm run dev -- -p 3001
```

## 📝 Environment Variables Reference

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| GEMINI_API_KEY | Google Gemini API key | Yes |
| DATABASE_URL | SQLite database path | No (defaults to sqlite:///./data/app.db) |
| SECRET_KEY | JWT secret key | Yes (for auth) |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| NEXT_PUBLIC_API_URL | Backend API URL | No (defaults to http://localhost:8000) |

## 🧪 Testing the Setup

### 1. Test Backend

Visit: http://localhost:8000/docs

You should see the FastAPI interactive documentation.

### 2. Test Frontend

Visit: http://localhost:3000

You should see the Inventix AI dashboard.

### 3. Test Draft Refinement

1. Navigate to "Draft Refinement" panel
2. Upload a text file or paste text
3. Click "Refine Draft"
4. View refined text and comparison

## 📦 Production Deployment

### Using Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up --build
```

### Manual Deployment

**Backend:**
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## 🔐 Security Notes

1. **Never commit `.env` files** - They contain sensitive keys
2. **Rotate API keys** - Regenerate keys periodically
3. **Use HTTPS** - In production, always use SSL/TLS
4. **OAuth Secrets** - Keep `client_secret_*.json` files out of version control

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Gemini API](https://ai.google.dev/docs)

## 💡 Tips

- Backend auto-reloads on code changes (--reload flag)
- Frontend has hot module replacement
- Check terminal logs for detailed error messages
- Use browser DevTools Network tab to debug API calls

## 🆘 Getting Help

If you encounter issues:

1. Check terminal output for error messages
2. Review the troubleshooting section above
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed
5. Check that both servers are running

---

**Happy Coding! 🚀**
