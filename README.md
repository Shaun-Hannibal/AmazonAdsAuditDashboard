# Amazon Advertising Audit Dashboard

A powerful tool for analyzing Amazon Advertising performance data, optimizing campaigns, and generating actionable insights.

---

## 📥 For Non-Technical Users: Getting Started

### Option 1: Using the Pre-Built Application (Easiest - No Coding Required)

**What you need:**
- A Mac or Windows computer
- The executable file from your coworker

**Steps:**

1. **Download the application**
   - Ask Shaun for the `Amazon_Dashboard` file (Mac) or `Amazon_Dashboard.exe` (Windows)
   - Save it to your Desktop or Downloads folder

2. **Run the application**
   - **Mac**: Double-click `Amazon_Dashboard`
     - If you see a security warning: Right-click → Open → Click "Open" again
   - **Windows**: Double-click `Amazon_Dashboard.exe`
     - If Windows Defender blocks it: Click "More info" → "Run anyway"

3. **Wait for the app to start**
   - First time takes 30-60 seconds (it's extracting files)
   - A browser window will open automatically with the dashboard
   - Future launches will be faster

4. **Start using the dashboard**
   - Upload your Amazon Advertising bulk files
   - The app will guide you through the analysis

**Your data is stored safely on your computer:**
- **Mac**: `~/Library/Application Support/AmazonDashboard/`
- **Windows**: `C:\Users\[YourName]\AppData\Roaming\AmazonDashboard\`

---

### Option 2: Running from Source Code (For Technical Users)

**What you need:**
- Basic comfort with command line
- 30 minutes for setup

#### Step 1: Install Python

**Mac:**
```bash
# Check if Python is already installed
python3 --version

# If not installed, download from python.org
# Or use Homebrew:
brew install python@3.11
```

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 or newer
3. **Important**: Check "Add Python to PATH" during installation
4. Click "Install Now"

#### Step 2: Download the Code

**Option A: Using Git (Recommended)**
```bash
# Install Git first if needed
# Mac: brew install git
# Windows: Download from git-scm.com

# Clone the repository
git clone https://github.com/Shaun-Hannibal/AmazonAdsAuditDashboard.git
cd AmazonAdsAuditDashboard
```

**Option B: Download ZIP**
1. Go to the GitHub repository
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file
5. Open Terminal (Mac) or Command Prompt (Windows)
6. Navigate to the extracted folder:
   ```bash
   cd path/to/AmazonAdsAuditDashboard
   ```

#### Step 3: Set Up Virtual Environment

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

**Windows:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# You should see (.venv) in your command prompt
```

#### Step 4: Install Dependencies

```bash
# Make sure your virtual environment is activated (you see .venv in prompt)
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Pandas (data analysis)
- Plotly (charts and graphs)
- And other required packages

#### Step 5: Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically open in your web browser at `http://localhost:8501`

#### Step 6: Stop the Dashboard

When you're done:
- Press `Ctrl+C` in the terminal to stop the server
- Type `deactivate` to exit the virtual environment

---

## 🔄 Daily Usage (After Initial Setup)

**Every time you want to use the dashboard:**

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Navigate to the project folder:
   ```bash
   cd path/to/AmazonAdsAuditDashboard
   ```
3. Activate virtual environment:
   - Mac: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Browser opens automatically → Start analyzing!

---

## 📊 What This Dashboard Does

- **Campaign Performance Analysis**: View metrics by campaign, ad group, and targeting
- **Search Term Analysis**: Identify high-performing search terms
- **Product Performance**: Track ASIN-level performance
- **Bid Optimization**: Get recommended bid adjustments based on performance
- **Campaign Creation**: Build new campaigns with advanced targeting
- **Bulk Operations**: Generate bulk upload files for Amazon Ads
- **Performance-Based Pauses**: Automatically identify underperforming entities

---

## 📁 File Requirements

The dashboard works with Amazon Advertising bulk export files:

**Required:**
- Sponsored Products bulk file (.xlsx)
- Sponsored Brands bulk file (.xlsx) - optional
- Sponsored Display bulk file (.xlsx) - optional

**Optional:**
- Sales & Traffic Report (for ASIN performance)
- Companion Targeting Export (for Sponsored Display metrics)

---

## 🆘 Troubleshooting

### "Command not found: python"
- **Mac**: Try `python3` instead of `python`
- **Windows**: Reinstall Python and check "Add to PATH"

### "Permission denied" when running
- **Mac**: Run `chmod +x Amazon_Dashboard` first
- Or right-click → Open instead of double-clicking

### "Module not found" errors
- Make sure virtual environment is activated (see `.venv` in prompt)
- Run `pip install -r requirements.txt` again

### Dashboard won't open in browser
- Manually go to: `http://localhost:8501`
- Check if another app is using port 8501

### App is slow or crashes
- Large files (>100MB) may take time to process
- Close other applications to free up RAM
- Consider using the database cache feature (automatic)

### "Out of memory" errors
- Your file might be too large for available RAM
- Try analyzing smaller date ranges
- Restart the app to clear memory

---

## 🔒 Data Privacy

- **All data stays on your computer** - nothing is uploaded to external servers
- Client configurations are stored locally
- Database cache improves performance for repeat analyses
- Your data is never shared or transmitted

---

## 👤 Cloud Accounts (Per-User Storage)

When deployed on Streamlit Community Cloud, the app can use Supabase Auth + Postgres to give each user an account so their clients and sessions are isolated.

### Setup (Maintainer)

- Create a Supabase project at https://supabase.com
- In Streamlit Cloud, add these Secrets:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
- In Supabase SQL Editor, run the following to create tables and Row Level Security (RLS):

```sql
create table if not exists client_configs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  client_name text not null,
  config jsonb not null,
  updated_at timestamptz not null default now(),
  unique (user_id, client_name)
);

create table if not exists client_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  client_name text not null,
  filename text not null,
  display_name text not null,
  timestamp timestamptz not null,
  created_date text,
  description text,
  data_types jsonb default '[]'::jsonb,
  session_data jsonb not null,
  unique (user_id, client_name, filename)
);

alter table client_configs enable row level security;
alter table client_sessions enable row level security;

create policy "owner_can_select_configs" on client_configs for select using (auth.uid() = user_id);
create policy "owner_can_upsert_configs" on client_configs for insert with check (auth.uid() = user_id);
create policy "owner_can_update_configs" on client_configs for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owner_can_delete_configs" on client_configs for delete using (auth.uid() = user_id);

create policy "owner_can_select_sessions" on client_sessions for select using (auth.uid() = user_id);
create policy "owner_can_upsert_sessions" on client_sessions for insert with check (auth.uid() = user_id);
create policy "owner_can_update_sessions" on client_sessions for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owner_can_delete_sessions" on client_sessions for delete using (auth.uid() = user_id);
```

### Usage (End Users)

- Open the app on Streamlit Community and sign up/in from the sidebar.
- After signing in, all client configurations and sessions you create are saved to your account only.
- Local desktop usage remains unchanged (files saved under your user data directory).

---

## 🚀 For Developers

### Project Structure
```
Dashboard/
├── app.py                  # Main application
├── database.py             # SQLite caching layer
├── run_dashboard.py        # Launcher for packaged app
├── package_app.py          # Build executable
├── amazon_dashboard.spec   # PyInstaller config
├── requirements.txt        # Python dependencies
├── assets/                 # Logo and images
│   └── hand_logo.png
├── clients/                # Client configurations (gitignored)
├── client_sessions/        # Saved sessions (gitignored)
└── .venv/                  # Virtual environment (gitignored)
```

### Key Features
- **Database caching**: Speeds up repeat analyses using SQLite
- **Multi-client support**: Switch between different client configurations
- **Session persistence**: Save and reload analysis states
- **Advanced filtering**: Multi-condition filters with AND/OR logic
- **Bulk export**: Generate Amazon-compatible bulk upload files

### Building Executables

See [PACKAGING_README.md](PACKAGING_README.md) for detailed instructions.

Quick build:
```bash
python package_app.py
```

Output in `dist/` folder.

---

## 📝 Version

Current version: **1.0.0**

---

## 👥 Support

For questions or issues:
1. Check the Troubleshooting section above
2. Contact Shaun (repository owner)
3. Review [PACKAGING_README.md](PACKAGING_README.md) for distribution details

---

## 📄 License

Private repository - Internal use only
