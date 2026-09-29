# BitSign: Lease Contract Management Dashboard

A full-stack web app for managing a retail chain's **commercial lease contracts**. It brings a live portfolio dashboard, a contract document library, and an **AI assistant (Amazon Bedrock Agent) that answers questions about the contracts and cites its sources** into one place.

Built in Python with [Reflex](https://reflex.dev) (Python compiled to a React frontend), backed by PostgreSQL (Amazon RDS), and deployed on AWS with Docker behind a load balancer.

<!-- Add screenshots of the dashboard, chat and contracts library here -->

---

## Features

### 📊 Portfolio dashboard
- KPIs computed live from the contracts database: total, active and expired contracts, contracts expiring in the next **30 / 60 / 90 days**, total and average monthly rent, and total security deposits.
- Charts: contracts by status (pie), monthly rent by status (bar), and expiry timeline (line).
- A contracts table with branch, status, monthly rent, and days until expiry, to spot renewals early.

### 💬 AI contract assistant
- Chat powered by an **Amazon Bedrock Agent** with a knowledge base over the contract PDFs.
- **Source citations**: each answer shows cards for the contract passages it used. Click a card to read the full text of the passage.
- **Conversation history** saved in PostgreSQL, so you can reopen past conversations.
- Async agent calls, with configurable timeouts and trace parsing.

### 📁 Contract library & upload
- Upload multiple PDFs at once to **Amazon S3**, with per-file progress and clear error messages (for example, missing S3 permissions).
- A searchable list of every contract stored in S3, with an in-app PDF preview through presigned URLs.
- A **"DB" details panel** that pulls the contract's key fields from RDS: status, branch, monthly rent, deposit, start and end dates, landlord, tenant, city, address, and payment method.

## Architecture

```
                  ┌───────────────────────────────┐
   Browser ──────▶│   Reflex app (Python)         │
  (React UI)      │   frontend :3000 / API :8000  │
                  └──┬───────────┬────────────┬───┘
                     │           │            │
           SQLAlchemy│      boto3│       boto3│
                     ▼           ▼            ▼
             ┌─────────────┐ ┌───────┐ ┌──────────────────┐
             │ PostgreSQL  │ │  S3   │ │  Bedrock Agent   │
             │ (RDS)       │ │ PDFs  │ │  + Knowledge     │
             │ contracts,  │ └───┬───┘ │    Base          │
             │ chat history│     │     └────────▲─────────┘
             └─────────────┘     └──────────────┘
                                  contract PDFs indexed
                                  for retrieval (RAG)
```

- **Dashboard:** the Reflex state runs aggregate SQL (`COUNT … FILTER`, `SUM`, `AVG`, `GROUP BY`) on the `contracts` table and converts the results into chart-ready data with computed vars.
- **Chat:** the user's message goes to `bedrock-agent-runtime.invoke_agent`, which returns a streamed completion plus citations. The citations become source cards, and the messages are saved to PostgreSQL.
- **Upload:** PDFs go to S3 under a `raw/` prefix, the source folder for the agent's knowledge base.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend + backend | Reflex 0.8 (Python → React), Radix UI, Recharts, TailwindCSS v4 |
| Database | PostgreSQL (Amazon RDS), SQLModel / SQLAlchemy, Alembic migrations |
| AI | Amazon Bedrock Agents + Knowledge Base (RAG with citations) |
| Storage | Amazon S3 (uploads, presigned previews) |
| Deployment | Docker, AWS load balancer |

## Project structure

```
bob/
├── bob.py              # App entry point, routes and global styles
├── state.py            # Dashboard state: KPIs and chart queries
├── chat_state.py       # Bedrock Agent chat, citations, history
├── chat_models.py      # Conversation / message tables
├── upload_state.py     # S3 upload, contract library, RDS details
├── models.py           # Dashboard tables
├── seed.py             # Dummy data for local development
├── pages/              # dashboard, chat, subir-archivo (upload), acerca (about)
└── components/         # sidebar, topbar, KPI cards, charts, tables
alembic/                # Database migrations
```

## Running locally

**Requirements:** Python 3.11, Node.js, PostgreSQL, and an AWS account with an S3 bucket and a Bedrock Agent (with a knowledge base).

```bash
git clone <this-repo>
cd bitsign-lease-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # fill in your own values
set -a && source .env && set +a

reflex db migrate             # create tables
python bob/seed.py            # optional: dummy dashboard data
reflex run                    # http://localhost:3000
```

> The dashboard reads from a `contracts` table that is filled by a separate contract-extraction pipeline, which is not part of this repository.

### Docker

```bash
docker build -t bitsign-dashboard .
docker run --env-file .env -p 3000:3000 -p 8000:8000 bitsign-dashboard
```

In production, set `API_URL` to the public backend address (for example, your load balancer's URL).

## Notes

- Built as a project for a retail client's legal and real-estate team. No client documents, data, or credentials are included. All configuration comes from environment variables (see `.env.example`).
- The UI is in Spanish, the language of its end users.

## Author

Eduardo Rey García Velasco
