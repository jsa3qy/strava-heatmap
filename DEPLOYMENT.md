# Deployment Guide: Auto-Updating Strava Heatmap Website

This guide will help you deploy your Strava heatmap as a live website that automatically updates daily with new activities.

## Prerequisites

- GitHub account
- Strava API credentials (Client ID and Client Secret)
- Your activities data (already generated locally)

## Step 1: Get Your Strava Refresh Token

Before deploying, you need to get your refresh token from your local setup:

1. Make sure you've run the scripts locally at least once (you've already done this!)

2. Check your `strava_tokens.json` file:
   ```bash
   cat strava_tokens.json
   ```

3. Copy the `refresh_token` value - you'll need this for GitHub Secrets

## Step 2: Create GitHub Repository

1. **Initialize git repository (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Strava heatmap generator"
   ```

2. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it something like `strava-heatmap`
   - Don't initialize with README (you already have files)
   - Click "Create repository"

3. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/strava-heatmap.git
   git branch -M main
   git push -u origin main
   ```

## Step 3: Configure GitHub Secrets

Add your Strava credentials as GitHub Secrets:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these three secrets:

   - **Name:** `STRAVA_CLIENT_ID`
     **Value:** Your Strava Client ID

   - **Name:** `STRAVA_CLIENT_SECRET`
     **Value:** Your Strava Client Secret

   - **Name:** `STRAVA_REFRESH_TOKEN`
     **Value:** Your refresh token from `strava_tokens.json`

## Step 4: Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Under **Source**, select:
   - **Branch:** `gh-pages`
   - **Folder:** `/ (root)`
3. Click **Save**

Note: The `gh-pages` branch will be created automatically by the first workflow run.

## Step 5: Run the Workflow

1. Go to **Actions** tab in your repository
2. Click on "Update Strava Heatmap" workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for it to complete (usually 1-2 minutes)

## Step 6: View Your Live Website!

Once the workflow completes:

1. Go to **Settings** → **Pages**
2. You'll see: "Your site is live at `https://YOUR_USERNAME.github.io/strava-heatmap/`"
3. Click the link to view your live heatmap!

## Automatic Updates

Your website will now automatically update:
- **Daily** at 6 AM UTC
- **Manually** whenever you trigger the workflow
- **On push** to the main branch (for testing)

The workflow will:
1. Fetch new activities from Strava
2. Update the GeoJSON data
3. Regenerate the heatmap
4. Update statistics
5. Rebuild the website
6. Deploy to GitHub Pages

## Local Testing

Before pushing changes, test locally:

```bash
# Generate stats
python3 generate_stats.py

# Generate heatmap
python3 generate_heatmap.py

# Build website
python3 build_website.py

# Open in browser
open index.html
```

## Customization

### Change Update Frequency

Edit `.github/workflows/update-heatmap.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # Change time/frequency here
```

Cron examples:
- `0 */6 * * *` - Every 6 hours
- `0 0 * * *` - Daily at midnight UTC
- `0 12 * * 1` - Weekly on Mondays at noon UTC

### Customize Heatmap Colors

Edit `generate_heatmap.py` around line 91 to adjust:
- `radius` - Line thickness (1-10)
- `blur` - Fuzziness (0-10)
- `min_opacity` - Transparency (0.0-1.0)

Then commit and push to trigger a rebuild.

### Customize Website Design

Edit `build_website.py` to modify:
- Colors, fonts, layout
- Statistics displayed
- Page title and branding

## Troubleshooting

### Workflow fails with "401 Unauthorized"

Your refresh token expired. Regenerate it:
1. Run `python3 strava_activities.py` locally
2. Get new refresh token from `strava_tokens.json`
3. Update the `STRAVA_REFRESH_TOKEN` secret on GitHub

### No new activities showing

- Check if you have new activities on Strava
- Manually trigger the workflow
- Check Actions tab for error logs

### Website not updating

- Ensure gh-pages branch exists
- Check GitHub Pages is enabled and pointing to gh-pages branch
- May take a few minutes for GitHub Pages to update after deployment

## Cost

- GitHub Actions: Free tier includes 2,000 minutes/month (this uses ~2 min/day = 60 min/month)
- GitHub Pages: Free for public repositories
- Strava API: Free (100 requests per 15 minutes limit)

## Privacy

Your repository should be public for GitHub Pages, but your credentials are safe:
- API credentials are stored in GitHub Secrets (encrypted)
- `config.json` and `strava_tokens.json` are gitignored
- Only the generated website files are public

If you want the entire repository private:
- Upgrade to GitHub Pro (free for students/educators)
- Or use alternative hosting (Netlify, Vercel)

## Next Steps

- Share your heatmap URL with friends!
- Customize the design to match your style
- Add more statistics or visualizations
- Consider adding filters by activity type or date range
