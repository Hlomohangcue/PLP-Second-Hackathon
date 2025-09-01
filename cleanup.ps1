# cleanup.ps1
Write-Host "🚀 Starting Git cleanup..."

# Step 0: Remove stale Git lock file if it exists
if (Test-Path ".git\index.lock") {
    Remove-Item ".git\index.lock" -Force
    Write-Host "✔ Removed stale .git/index.lock"
}

# Step 1: Add backend/.env to .gitignore
Add-Content -Path ".gitignore" -Value "backend/.env"
Write-Host "✔ Added backend/.env to .gitignore"

# Step 2: Stop tracking backend/.env
git rm --cached backend/.env
git commit -m "Remove backend/.env from tracking and add to .gitignore"

# Step 3: Install git-filter-repo if missing
pip show git-filter-repo > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installing git-filter-repo..."
    pip install git-filter-repo
}

# Step 4: Rewrite history to remove backend/.env
Write-Host "🧹 Cleaning Git history..."
git filter-repo --path backend/.env --invert-paths

# Step 5: Force push cleaned repo
Write-Host "⬆️ Force pushing cleaned branch..."
git push origin main --force

Write-Host "✅ Cleanup complete! Your repo is safe and secrets removed."