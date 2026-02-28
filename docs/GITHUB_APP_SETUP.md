![ievo-eva](ievo-eva-logo.png)

# GitHub App Setup for Eva
## Why GitHub App instead of PAT?

- Not tied to a person (won't break when someone leaves the team)
- Separate identity: commits from `ievo-eva[bot]`
- Granular permissions (only what's needed)
- Doesn't occupy a seat in the organization
- Higher rate limit than PAT (5000 → 15000 req/h)

---

## Step 1: Create the App

1. Open: https://github.com/organizations/ievo-ai/settings/apps/new
   (or GitHub → ievo-ai → Settings → Developer settings → GitHub Apps → New)

2. Fill in:

| Field | Value |
|-------|-------|
| **App name** | `ievo-eva` |
| **Description** | Meta-evolution Mother agent for iEvo platform |
| **Homepage URL** | `https://ievo.ai` |
| **Webhook** | ❌ Uncheck "Active" (Eva polls on its own, no webhook needed) |

3. **Permissions** (Repository permissions):

| Permission | Access | Why |
|-----------|--------|-----|
| **Issues** | Read | Read issues for analysis |
| **Pull requests** | Read & Write | Read PR comments + create PRs |
| **Contents** | Read & Write | Read files + push branches for PRs |
| **Metadata** | Read | Basic repo info (automatic) |

4. **Where can this app be installed?** → Only on this account

5. **Create GitHub App**

---

## Step 2: Generate Private Key

1. After creation → go to App settings
2. Scroll down to **Private keys**
3. **Generate a private key** → a `.pem` file will be downloaded
4. Store it in a safe location

---

## Step 3: Install App on repositories

1. In App settings → **Install App** (left panel)
2. Select organization **ievo-ai**
3. **Only select repositories** → select:
   - `cli`
   - `marketplace`
   - `sdk`
   - `eva`
   - `ievo.ai`
4. **Install**

---

## Step 4: Obtain Installation Token

GitHub App authenticates via JWT → Installation Token.
For GitHub Actions the easiest way is through an action:

### GitHub Actions (recommended)

Add secrets to `ievo-ai/eva` → Settings → Secrets → Actions:

| Secret | Value |
|--------|-------|
| `APP_ID` | App ID (visible on the App page) |
| `APP_PRIVATE_KEY` | Contents of the `.pem` file |

Then update workflows — replace PAT with App token:

```yaml
# Instead of:
# env:
#   EVA_GITHUB_TOKEN: ${{ secrets.EVA_GITHUB_TOKEN }}

# Use:
- name: Generate token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    owner: ievo-ai

- name: Run Eva scan
  env:
    EVA_GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    docker run --rm -e EVA_GITHUB_TOKEN eva:local scan
```

### Local testing / self-hosted

You can generate the token via a script:

```bash
# Install
pip install PyJWT cryptography

# Generate (see scripts/generate-app-token.py)
python scripts/generate-app-token.py \
  --app-id 123456 \
  --private-key path/to/key.pem \
  --org ievo-ai
```

---

## Step 5: Update secrets

### For GitHub Actions
- Remove: `EVA_GITHUB_TOKEN`
- Add: `APP_ID`, `APP_PRIVATE_KEY`

### For self-hosted Docker
```env
# .env
EVA_APP_ID=123456
EVA_APP_PRIVATE_KEY_PATH=/path/to/key.pem
```

---

## Verification

```bash
# In Actions: trigger the workflow manually
# Eva logs should show:
#   ✓ github_issues: N signals
#   (no 401/403 errors)
```

---

## Quick start (PAT for quick testing)

If you want to get started quickly, you can use a Fine-grained PAT for now:

1. https://github.com/settings/tokens?type=beta
2. **Token name**: `eva-test`
3. **Resource owner**: `ievo-ai`
4. **Repository access**: Only select → all ievo repos
5. **Permissions**: Issues (read), Pull requests (read), Contents (read)
6. **Generate token**
7. Add to secrets as `EVA_GITHUB_TOKEN`

Switch to GitHub App once everything is working.
