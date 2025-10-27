# .streamlit Configuration Directory

This directory contains Streamlit configuration files for the LOR/LOA Generator.

## Files

### `config.toml` ✅ (Committed to Git)
App configuration settings:
- Theme colors
- Server settings
- Browser configuration
- Performance settings

**Safe to commit** - Contains no sensitive data

### `secrets.toml.template` ✅ (Committed to Git)
Template showing what secrets are needed:
- Password placeholders
- Pricing structure
- Configuration examples

**Safe to commit** - Contains only placeholders

### `secrets.toml` ⚠️ (NEVER COMMIT!)
Your actual secrets:
- Real passwords
- Actual pricing
- Sensitive configuration

**PROTECTED BY .gitignore** - Never committed to git

## Setup Instructions

### For Local Development:

1. Copy the template:
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

2. Edit `secrets.toml` with your actual values:
   ```bash
   nano .streamlit/secrets.toml
   ```

3. Fill in:
   - Your actual passwords
   - Your real pricing
   - Any custom configuration

4. Run the app:
   ```bash
   streamlit run app.py
   ```

### For Streamlit Cloud Deployment:

1. Open your `secrets.toml` file locally (after you've created it)

2. Copy the ENTIRE contents

3. Go to Streamlit Cloud:
   - Open your app settings
   - Click "Secrets"
   - Paste the entire contents
   - Click "Save"

4. Deploy or reboot your app

## Security Notes

**CRITICAL**: The `secrets.toml` file contains:
- Passwords for authentication
- Pricing information (business sensitive)
- Access control data

**Never**:
- ❌ Commit `secrets.toml` to git
- ❌ Share `secrets.toml` via email/messaging
- ❌ Store in shared drives
- ❌ Include in screenshots

**Always**:
- ✅ Keep local copy secure
- ✅ Use strong passwords
- ✅ Rotate passwords regularly
- ✅ Use Streamlit Cloud secrets for deployment

## Troubleshooting

### "Secrets not configured" error

**Local development**:
- Ensure `.streamlit/secrets.toml` exists
- Check file permissions
- Verify TOML syntax is correct

**Streamlit Cloud**:
- Check secrets are configured in app settings
- Ensure no syntax errors in TOML
- Reboot app after changing secrets

### "Permission denied" error

```bash
chmod 600 .streamlit/secrets.toml
```

### Verify secrets are protected:

```bash
git status
# secrets.toml should NOT appear in untracked files
```

## Questions?

See main README.md for full documentation.
