# How to Upload to GitHub

Your project is now ready to be uploaded to GitHub! Follow these steps:

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Choose a repository name (e.g., "skating-technique-analyzer")
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

### Option A: Using HTTPS (Recommended for beginners)

```bash
cd "C:\Users\arnav\OneDrive\Documents\code\skating code\skating code"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPO_NAME` with your repository name.

### Option B: Using SSH (If you have SSH keys set up)

```bash
cd "C:\Users\arnav\OneDrive\Documents\code\skating code\skating code"
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Authenticate

When you run `git push`, you may be prompted to authenticate:
- **HTTPS**: You'll need a Personal Access Token (not your password)
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate a new token with `repo` permissions
  - Use this token as your password when prompted

- **SSH**: Should work automatically if you have SSH keys configured

## Step 4: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files there!

## Future Updates

To update your repository after making changes:

```bash
cd "C:\Users\arnav\OneDrive\Documents\code\skating code\skating code"
git add .
git commit -m "Description of your changes"
git push
```

## Quick Command Reference

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes (if working on multiple computers)
git pull
```

## Troubleshooting

### If you get "remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_REPO_URL
```

### If you need to change the branch name
```bash
git branch -M main
```

### If push is rejected
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

