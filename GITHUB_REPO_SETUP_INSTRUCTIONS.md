# GitHub Repository Setup Instructions

## Authentication with GitHub CLI

Before creating a repository, you need to authenticate with GitHub CLI. Run the following command:

```bash
gh auth login
```

You'll be prompted to choose an authentication method:
1. Paste an authentication token (recommended for CI/CD or if you have SSO requirements)
2. Authenticate via a web browser

For browser authentication:
- Select "GitHub.com"
- Choose "HTTPS" as protocol
- Choose to authenticate via browser
- Log in to your GitHub account in the browser when prompted

## Creating the Repository

After authentication, run:

```bash
# Navigate to your project directory
cd /home/joshu/unified-theming

# Create a new repository on GitHub
gh repo create unified-theming --public --description "Unified Theming System for GTK, Qt, and containerized applications"

# Or for a private repository, use:
# gh repo create unified-theming --private --description "Unified Theming System for GTK, Qt, and containerized applications"

# Push your existing code to the new repository
git remote add origin https://github.com/USERNAME/unified-theming.git
git branch -M main
git push -u origin main
```

Replace USERNAME with your GitHub username.

## Alternative: Using GitHub Token

If you prefer using a token (recommended for automation), generate a personal access token from GitHub with the following scopes:
- repo: Full control of private repositories
- workflow: Update GitHub Actions
- write:org, read:org, admin:org (if creating organization repositories)

Then authenticate using:
```bash
gh auth login --with-token < token_file
```

## Verification

After creating the repository, verify everything is set up correctly:

```bash
# Check the remote
git remote -v

# Check the status
git status

# Verify connection to GitHub
gh repo view
```