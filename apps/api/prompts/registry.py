import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.prompts.models import Prompt

logger = structlog.get_logger()


class PromptRegistry:
    async def get_prompt(
        self,
        db: AsyncSession,
        name: str,
        tenant_id: str | None = None,
    ) -> Prompt | None:
        if tenant_id:
            result = await db.execute(
                select(Prompt)
                .where(
                    Prompt.name == name,
                    Prompt.tenant_id == tenant_id,
                    Prompt.is_active,
                )
                .order_by(Prompt.version.desc())
                .limit(1)
            )
            prompt = result.scalar_one_or_none()
            if prompt:
                return prompt

        result = await db.execute(
            select(Prompt)
            .where(
                Prompt.name == name,
                Prompt.tenant_id.is_(None),
                Prompt.is_active,
            )
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_prompt_version(
        self,
        db: AsyncSession,
        name: str,
        template: str,
        tenant_id: str | None = None,
    ) -> Prompt:
        result = await db.execute(
            select(Prompt)
            .where(
                Prompt.name == name,
                Prompt.tenant_id == tenant_id,
            )
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        new_version = (latest.version + 1) if latest else 1

        if latest:
            latest.is_active = False

        prompt = Prompt(
            name=name,
            version=new_version,
            tenant_id=tenant_id,
            template=template,
            is_active=True,
        )
        db.add(prompt)
        logger.info("prompt_created", name=name, version=new_version, tenant_id=tenant_id)
        return prompt

    async def rollback(
        self,
        db: AsyncSession,
        name: str,
        version: int,
        tenant_id: str | None = None,
    ) -> Prompt | None:
        result = await db.execute(
            select(Prompt).where(
                Prompt.name == name,
                Prompt.version == version,
                Prompt.tenant_id == tenant_id,
            )
        )
        target = result.scalar_one_or_none()
        if not target:
            return None

        result = await db.execute(
            select(Prompt).where(
                Prompt.name == name,
                Prompt.tenant_id == tenant_id,
                Prompt.is_active,
            )
        )
        current = result.scalar_one_or_none()
        if current:
            current.is_active = False

        target.is_active = True
        logger.info("prompt_rollback", name=name, version=version, tenant_id=tenant_id)
        return target
