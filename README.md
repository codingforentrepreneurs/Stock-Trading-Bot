# Stock-Trading-Bot
Extract data, analyze, and decide on stocks in the market using Django, Celery, TimescaleDB, Jupyter, OpenAI, and more.

__Tech Stack__:
- [Python 3.12](https://github.com/python)
- [Django](https://github.com/django/django) (`pip install "Django>=5.1,<5.2"`)
- [Django Timescaledb](https://github.com/jamessewell/django-timescaledb) (`pip install django-timescaledb`)
- [Python requests](https://github.com/psf/requests) (`pip install requests`)
- [Jupyter](https://jupyter.org/) (`pip install jupyter`)
- [Psycopg Binary Release](https://pypi.org/project/psycopg/) (`pip install "psycopg[binary]"`)
- More to come

## Getting Started

Download the following:
- [git](https://git-scm.com/)
- [VSCode](https://code.visualstudio.com/) (or [Cursor](https://cursor.com/))
- Docker Desktop
- [Python](https://www.python.org/downloads/)

Open a command line (Terminal, VSCode Terminal, Cursor Terminal, Powershell, etc)

Clone this Repo
```bash
mkdir -p ~/dev/stock-trading-bot
cd ~/dev/stock-trading-bot
git clone https://github.com/codingforentrepreneurs/Stock-Trading-Bot .
```

Checkout the start branch
```
git checkout start
rm -rf .git
```

Create a Python vitual environment
_macOS/Linux/WSL_
```bash
python3.12 -m venv venv
source venv/bin/activate
```

_windows powershell_
```powershell
c:\Path\To\Python312\python.exe -m venv venv
.\venv\Scripts\activate
```

Install requirements
```
(venv) python -m pip install -r requirements.txt
```

Docker Compose Up (for local TimescaleDB and Redis)
```
docker compose -f compose.yaml up -d
```
> If you don't have Docker, use [TimescaleDB Cloud](tsdb.co/justin) and [Upstash Redis](https://upstash.com/?utm_source=cfe)

Create `.env` in project root
```
mkdir -p ~/dev/stock-trading-bot
echo "" >> .env
```

Add `DATABASE_URL` and `REDIS_URL` to `.env` (these are based on the `compose.yaml` file):
```
DATABASE_URL="postgresql://postgres:postgres@localhost:5431/postgres"
REDIS_URL="redis://localhost:6378"
```


