#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."

uv run python -c "
from apps.api.core.database import engine
from apps.api.tenants.models import Base
import apps.api.conversation.models
import apps.api.monitoring.models
import apps.api.prompts.models
import apps.api.rag.models
import apps.api.tenants.models_ext
import apps.api.tools.models
import apps.api.widget.models

import asyncio

async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('All tables created.')

asyncio.run(run())
"

echo "Migration complete."
