# Course Advisor Backend

This is the backend service for the Course Advisor application, built using FastAPI, SQLAlchemy, LlamaIndex, and OpenAI.

For a comprehensive guide of the backend architecture, data models, auth system, and AI integration, please refer to the main documentation file:
👉 **[BACKEND_OVERVIEW.md](../BACKEND_OVERVIEW.md)**

## Architecture Quick Summary
- **Framework**: FastAPI
- **Design Pattern**: Clean Architecture / DDD (Domain-Driven Design)
- **Database**: PostgreSQL / SQLite (via SQLAlchemy ORM & Alembic migrations)
- **AI Integrations**: LlamaIndex, OpenAI (`gpt-4o`), Tavily Search API
- **Auth**: JWT tokens (`HS256`), password hashing (`pwdlib`)
- **Caching & Chat History**: Redis
