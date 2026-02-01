# 🪟 Windows Quick Start Guide - Inventix AI

## 🎯 Easiest Way - Use Batch Scripts

### Step 1: Double-click `deploy.bat`

This script will:
- ✅ Check if Docker is running
- ✅ Create `.env` file if missing
- ✅ Open `.env` in Notepad for editing
- ✅ Build and start all services
- ✅ Open the app in your browser

### Step 2: Add Your API Key

When Notepad opens, add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
Save and close Notepad.

### Step 3: You're Done! 🎉

The app will open automatically at http://localhost:3000

---

## 📋 Available Batch Scripts

| Script | What It Does |
|--------|--------------|
| **`deploy.bat`** | 🚀 Build and start everything |
| **`stop.bat`** | ⏹️ Stop all services |
| **`logs.bat`** | 📜 View real-time logs |
| **`status.bat`** | ✅ Check service health |

**Just double-click** any `.bat` file to run it!

---

## 💻 Manual Commands (Windows CMD)

If you prefer using CMD directly:

### Initial Setup

```cmd
REM 1. Open CMD and navigate to project
cd G:\INVENTIX

REM 2. Create environment file
copy .env.example .env

REM 3. Edit .env and add your GEMINI_API_KEY
notepad .env
```

### Start Services

```cmd
docker-compose up -d
```

### View Logs

```cmd
docker-compose logs -f
```

### Stop Services

```cmd
docker-compose down
```

### Check Status

```cmd
docker-compose ps
```

---

## 🌐 Access Your Application

Once running, open these URLs in your browser:

| Service | URL |
|---------|-----|
| **Frontend** (Main App) | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **API Health Check** | http://localhost:8000/health |

---

## 🔧 Troubleshooting

### Problem: "Docker is not running"

**Solution:**
1. Open Docker Desktop from Start Menu
2. Wait for Docker icon in system tray to turn green
3. Run `deploy.bat` again

### Problem: "Port 3000 or 8000 is already in use"

**Solution:**
```cmd
REM Find what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000

REM Stop the process (use PID from above)
taskkill /PID <process_id> /F
```

### Problem: Backend health check fails

**Solution:**
```cmd
REM Check backend logs
docker-compose logs backend

REM Verify your API key is set
docker-compose exec backend env | findstr GEMINI_API_KEY
```

### Problem: Need to start fresh

**Solution:**
```cmd
REM Clean everything
docker-compose down -v --rmi all
docker system prune -a

REM Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Full Documentation

For complete documentation:
- **Windows CMD Commands**: `DOCKER_WINDOWS_CMD.md`
- **Deployment Guide**: `DOCKER_DEPLOYMENT.md`
- **Quick Reference**: `DOCKER_QUICKSTART.md`

---

## ✅ Prerequisites

Before running, ensure you have:

1. ✅ **Docker Desktop for Windows** installed
   - Download: https://www.docker.com/products/docker-desktop/

2. ✅ **WSL 2** enabled (Docker Desktop will prompt if needed)

3. ✅ **Gemini API Key** from Google AI Studio
   - Get it: https://aistudio.google.com/

---

## 🎮 Daily Usage

```cmd
REM Morning - Start services
deploy.bat

REM During work - Check status
status.bat

REM Debug issues - View logs
logs.bat

REM Evening - Stop services
stop.bat
```

---

## 🔄 After Code Changes

```cmd
REM Rebuild and restart
docker-compose down
docker-compose up -d --build
```

Or just double-click **`deploy.bat`** again!

---

## 💡 Pro Tips

1. **Keep Docker Desktop Running** - Pin it to taskbar
2. **Check System Tray** - Green Docker icon = ready
3. **Use PowerShell** - For advanced features
4. **Run as Administrator** - If you get permission errors
5. **Bookmark URLs** - Save time accessing services

---

## 🆘 Need Help?

1. Run `status.bat` to check what's wrong
2. Run `logs.bat` to see detailed error messages
3. Check `DOCKER_WINDOWS_CMD.md` for more commands
4. Restart Docker Desktop
5. Restart your computer (if all else fails)

---

**Happy Deploying! 🚀**

*Your application should now be running at http://localhost:3000*
