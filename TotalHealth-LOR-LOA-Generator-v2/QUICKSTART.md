# 🚀 QUICKSTART GUIDE

**Get your LOR/LOA Generator running in 5 minutes!**

---

## ⚡ Option 1: Local Development (Fastest Way to Test)

### Step 1: Install Dependencies (2 minutes)

```bash
cd TotalHealth-LOR-LOA-Generator-v2/
pip install -r requirements.txt
```

### Step 2: Configure Secrets (2 minutes)

```bash
# Copy the template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit with your values
nano .streamlit/secrets.toml
```

**Minimum required changes**:
- Change `password = "YourSecurePassword123!"`
- Update booth prices if needed
- Update add-on prices if needed

### Step 3: Run! (1 minute)

```bash
streamlit run app.py
```

**That's it!** App opens at http://localhost:8501

---

## ☁️ Option 2: Deploy to Streamlit Cloud (Production)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select repository: `THOLOR-LOAGeneratorRebuildOct2025`
4. Branch: `claude/review-uploaded-repo-011CUWqxHU8XAd34skRorERT`
5. Main file: `TotalHealth-LOR-LOA-Generator-v2/app.py`

### Step 3: Add Secrets

1. Click "Advanced settings" → "Secrets"
2. Copy contents from your local `.streamlit/secrets.toml`
3. Paste into secrets box
4. Click "Deploy"

**Done!** Your app will be live in 2-3 minutes.

---

## 🧪 First Test

### Login

1. Enter one of your passwords from `secrets.toml`
2. Click "Login"

### Generate Your First Letter

1. Mode: **Single Event**
2. Document Type: **LOR**
3. Search: "ASCO"
4. Select: First ASCO event
5. Company: "Test Company Inc"
6. Booth: **Standard Booth (1-Day)**
7. Click: **Generate Documents**
8. Download both DOCX and PDF

**Success!** You just generated your first document.

---

## 📚 Next Steps

### Learn More:
- **README.md** - Full documentation
- **DEPLOYMENT_CHECKLIST.md** - Complete deployment guide
- **DEPLOYMENT_GUIDE.md** - Detailed Streamlit Cloud setup

### Customize:
- Add/remove events in `config/events.py`
- Update pricing in `.streamlit/secrets.toml`
- Modify templates in `config/settings.py`

### Test Everything:
- Try all 3 passwords
- Generate LOR and LOA
- Test multi-meeting packages
- Try different booths and add-ons
- Test discount options

---

## 🆘 Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Secrets not configured"
```bash
# Make sure file exists
ls .streamlit/secrets.toml

# If not, copy template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

### "Logo not found"
```bash
# Verify assets exist
ls assets/
# Should show: TH Logo.png, sarah_signature.jpg
```

### "Password incorrect"
- Check `.streamlit/secrets.toml` for correct password
- Ensure quotes around password
- No extra spaces

---

## ✅ You're Ready!

**Local URL**: http://localhost:8501
**Cloud URL**: (will get after deployment)

**Three users**:
- Admin (main password)
- Sarah (sarah_password)
- Allison (allison_password)

**Three modes**:
- Single Event
- Multi-Meeting Package
- Excel Bulk (coming soon)

**Two document types**:
- LOR (Letter of Request)
- LOA (Letter of Agreement)

---

**Questions?** Check README.md or DEPLOYMENT_GUIDE.md

**Ready to deploy?** Follow DEPLOYMENT_CHECKLIST.md

---

**Total Health Conferencing - Professional Document Generation** 📄
