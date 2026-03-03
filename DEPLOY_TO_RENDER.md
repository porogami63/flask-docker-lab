# TaskFlow - Deployment Guide for Render

## Prerequisites
- GitHub account with your code pushed to a repository
- Render account (free tier available at render.com)
- MongoDB Atlas account with credentials

## Step 1: Push Your Code to GitHub

```bash
# Initialize git (if not already done)
cd d:/group/flask-docker-lab
git init
git add .
git commit -m "Initial commit - TaskFlow application"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/flask-docker-lab.git
git branch -M main
git push -u origin main
```

## Step 2: Create a Render Account and Connect GitHub

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click "New +" → "Web Service"
4. Select "Build and deploy from a Git repository"
5. Authenticate with GitHub and select your `flask-docker-lab` repository
6. Choose the repository branch (usually `main`)

## Step 3: Configure Web Service Settings

### Basic Settings:
- **Name**: `taskflow` (or your preferred name)
- **Environment**: `Docker`
- **Dockerfile**: `Dockerfile.render`
- **Build Filter Branch**: (leave empty to build all branches)
- **Auto-deploy**: Enable (optional, for auto-deployment on push)

### Instance Type:
- **Starter** (free): Spins down after 15 minutes of inactivity
- **Standard** (paid): Always running

## Step 4: Set Environment Variables

In the Render dashboard, scroll to **Environment Variables** and add:

```
MONGO_URI = mongodb+srv://admin:admin@cluster0.b6fwowm.mongodb.net/FlaskApp-Docker?retryWrites=true&w=majority&authSource=admin&tls=true
MONGO_DB = FlaskApp-Docker
PORT = 10000
FLASK_ENV = production
```

**Note**: Replace the MONGO_URI with your actual MongoDB Atlas credentials if different.

## Step 5: Deploy

1. Click the **"Create Web Service"** button
2. Render will automatically:
   - Build the Docker image
   - Deploy the container
   - Assign a public URL (something like `taskflow.onrender.com`)

3. Wait for the build to complete (typically 5-15 minutes)
4. Once deployed, view your app at the provided URL

## Step 6: Troubleshooting

### View Logs:
- In the Render dashboard, click your service
- Go to the **"Logs"** tab to see deployment and runtime logs

### Common Issues:

**Build fails with "Dockerfile.render not found":**
- Make sure `.gitignore` doesn't exclude the Dockerfile
- Ensure you've pushed the file to GitHub

**App crashes with "MONGO_URI not found":**
- Verify environment variables in Render dashboard
- Check MongoDB Atlas network access (allow 0.0.0.0/0)

**Port binding error:**
- Ensure Dockerfile.render uses port 10000
- Render expects services to bind to a PORT environment variable

**Static files not serving:**
- Verify the `public/` folder is in the repo
- Check that `index.html` exists in the public folder

### Cold Start Delay:
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep may take 30-60 seconds
- Upgrade to Standard tier for instant startup

## Step 7: Accessing Your Application

Once deployed:
- **Web App URL**: `https://taskflow.onrender.com`
- Add tasks with timestamps
- Set alarms for reminders
- All data persists in MongoDB Atlas

## Alternative: Using Render's Blueprint (Automatic Setup)

1. Create a `render.yaml` file in your repository root (already included)
2. Go to Render Dashboard → "New +" → "Infrastructure as Code"
3. Select your GitHub repo
4. Render automatically parses `render.yaml` and configures your service
5. Add required environment variables and deploy

## Updating Your Application

After making changes:

```bash
# Commit and push changes
git add .
git commit -m "Your changes description"
git push origin main
```

If auto-deploy is enabled, Render will automatically rebuild and redeploy.

## Free Tier Limits

- Apps spin down after 15 minutes of inactivity
- Limited to 750 free tier hours per month
- Shared CPU and 512MB RAM
- Great for hobby projects and testing!

## Upgrade to Production

For a production app:
- Upgrade to **Standard** tier for 24/7 uptime
- Use **PostgreSQL** or managed MongoDB instead of free tier
- Add custom domain
- Enable SSL/TLS (automatic with Render)

---

**Questions?** Check Render's documentation at [render.com/docs](https://render.com/docs)
