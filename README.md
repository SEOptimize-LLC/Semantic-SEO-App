# 🎯 Semantic SEO Platform

**Build Topical Authority with Koray Tuğberk GÜBÜR's Framework**

A comprehensive Semantic SEO platform that implements the complete workflow from Topical Mapping through Content Briefs, Publication Management, and Performance Tracking.

---

## 📚 Overview

This platform is based on Koray's Semantic SEO framework, which focuses on:

- **Topical Authority** = Topical Coverage × Historical Data
- **Entity-Attribute Mapping** with PPR scoring (Prominence, Popularity, Relevance)
- **CorelIS Framework** for content briefs (Vector, Hierarchy, Structure, Connection)
- **Momentum-Based Publishing** for authority signals

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation

1. **Clone/Navigate to the project:**
   ```bash
   cd "Marketing/Roger SEO/Scripts/Semantic SEO App"
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Copy example env file
   copy .env.example .env   # Windows
   cp .env.example .env     # Mac/Linux
   
   # Edit .env and add your API keys
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser:**
   The app will open automatically at `http://localhost:8501`

---

## ☁️ Streamlit Cloud Deployment

Deploy this app for free on Streamlit Cloud in minutes!

### Step 1: Fork/Clone Repository

1. Go to https://github.com/SEOptimize-LLC/Semantic-SEO-App
2. Fork the repository to your GitHub account

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your forked repository
5. Set the main file path to `app.py`
6. Click "Deploy!"

### Step 3: Configure Secrets (API Keys)

**This is the most important step!** Configure your API keys securely:

1. In your deployed app, click **"Manage app"** (bottom right)
2. Click **"Settings"** → **"Secrets"**
3. Add your secrets in TOML format:

```toml
# Required: At least one AI provider
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"

# Optional: Additional AI providers
OPENAI_API_KEY = "sk-your-openai-key"
ANTHROPIC_API_KEY = "sk-ant-your-anthropic-key"
GOOGLE_API_KEY = "your-google-ai-key"

# Optional: Default settings
DEFAULT_AI_PROVIDER = "openrouter"
DEFAULT_MODEL = "anthropic/claude-3-sonnet"

# Optional: SERP analysis
SERPER_API_KEY = "your-serper-key"

# Optional: Cloud sync
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

4. Click **"Save"** - your app will restart with the new secrets

### Secrets Reference

| Secret Key | Required | Description |
|------------|----------|-------------|
| `OPENROUTER_API_KEY` | ⭐ At least one | [OpenRouter](https://openrouter.ai) - Access multiple models |
| `OPENAI_API_KEY` | ⭐ At least one | [OpenAI](https://platform.openai.com) - GPT models |
| `ANTHROPIC_API_KEY` | ⭐ At least one | [Anthropic](https://console.anthropic.com) - Claude models |
| `GOOGLE_API_KEY` | ⭐ At least one | [Google AI](https://makersuite.google.com) - Gemini models |
| `DEFAULT_AI_PROVIDER` | Optional | `openrouter`, `openai`, `anthropic`, or `google` |
| `DEFAULT_MODEL` | Optional | Model ID for default provider |
| `SERPER_API_KEY` | Optional | [Serper](https://serper.dev) - SERP analysis |
| `SUPABASE_URL` | Optional | [Supabase](https://supabase.com) - Cloud database sync |
| `SUPABASE_KEY` | Optional | Supabase anon key |
| `DEBUG_MODE` | Optional | `true` or `false` |

### Important Notes

- **Secrets are encrypted** and never exposed in your code
- The app reads secrets automatically via `st.secrets`
- Database persists in `/data/` during the session
- For permanent data, configure Supabase cloud sync

---

## 🔑 API Keys Required

At minimum, you need **one AI provider** configured:

| Provider | Get API Key |
|----------|-------------|
| **OpenRouter** (Recommended) | [openrouter.ai](https://openrouter.ai) |
| OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) |
| Google (Gemini) | [makersuite.google.com](https://makersuite.google.com/app/apikey) |

**Optional integrations:**
- Google Search Console (for analytics)
- Serper API (for SERP analysis)

---

## 📁 Project Structure

```
Semantic SEO App/
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── ARCHITECTURE.md        # Detailed architecture documentation
│
├── config/                # Configuration modules
│   ├── settings.py        # App settings management
│   ├── ai_providers.py    # AI provider configurations
│   └── database.py        # Database configuration
│
├── utils/                 # Utility modules
│   ├── database.py        # SQLAlchemy models
│   ├── session_state.py   # Streamlit session management
│   └── export.py          # Export utilities
│
├── modules/               # Feature modules
│   └── project/           # Project management
│       └── service.py     # Project CRUD operations
│
├── pages/                 # Streamlit pages
│   ├── 1_🏠_Dashboard.py
│   ├── 2_🗺️_Topical_Maps.py
│   ├── 3_📝_Content_Briefs.py
│   ├── 4_📅_Publication_Manager.py
│   ├── 5_📊_Analytics.py
│   ├── 6_🔗_Link_Network.py
│   └── 7_⚙️_Settings.py
│
└── data/                  # Data directory (auto-created)
    ├── semantic_seo.db    # SQLite database
    └── exports/           # Export files
```

---

## 📱 Features

### Phase 1: Foundation ✅
- [x] Project management (CRUD)
- [x] SQLite database with models
- [x] Multi-provider AI integration
- [x] Settings and API key management
- [x] Session state management
- [x] Export utilities

### Phase 2: Topical Map Builder 🚧
- [ ] AI entity discovery
- [ ] PPR attribute scoring
- [ ] Core/Outer section management
- [ ] Visual map editor
- [ ] Export options

### Phase 3: Content Brief Generator 🚧
- [ ] CorelIS framework implementation
- [ ] Question engineering
- [ ] Meta element generation
- [ ] Brief validation
- [ ] Authorship codes

### Phase 4: Publication Manager 🚧
- [ ] Kanban board
- [ ] Momentum planning
- [ ] State change launch
- [ ] URL management

### Phase 5: Internal Linking 🚧
- [ ] Link graph visualization
- [ ] Orphan detection
- [ ] Link recommendations
- [ ] Anchor text generator

### Phase 6: Analytics 🚧
- [ ] GSC integration
- [ ] 3-Column query analysis
- [ ] Topical authority metrics
- [ ] N-gram analysis

---

## 📖 Key Concepts

### Source Context
Who you are and how you make money. This defines the "lens" through which you cover your topic.

### Central Entity
The main subject matter of your website. Appears site-wide in your N-grams and content network.

### Central Search Intent
The unification of Source Context + Central Entity.

### Topical Map
A semantic blueprint covering every attribute of an entity:
- **Core Section**: Directly tied to monetization
- **Outer Section**: Builds historical data and trust

### PPR Scoring
- **Prominence**: Can the entity be defined without this attribute?
- **Popularity**: Is there high search demand?
- **Relevance**: Does it fit your source context?

### CorelIS Framework
- **Contextual Vector**: Logical flow of questions/headings
- **Contextual Hierarchy**: H2/H3/H4 weighting
- **Contextual Structure**: Format instructions (FS, PAA, lists)
- **Contextual Connection**: Internal link planning

---

## 🛠 Development

### Running in Development Mode

```bash
streamlit run app.py --server.runOnSave true
```

### Database Reset

The database can be reset from Settings > Data Management, or:

```python
from config.database import reset_db
reset_db()
```

### Adding New Modules

1. Create module directory in `modules/`
2. Add `__init__.py` with exports
3. Create `service.py` with business logic
4. Register in `modules/__init__.py`

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

Based on the Semantic SEO framework developed by **Koray Tuğberk GÜBÜR**.

- [Holistic SEO & Digital](https://www.holisticseo.digital/)
- Topical Authority Course

---

## 📞 Support

For issues and feature requests, please open an issue on the repository.

---

*Built with ❤️ for the Semantic SEO community*