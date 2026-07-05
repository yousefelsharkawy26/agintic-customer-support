import glob
import re


def refactor_models():
    files = glob.glob("apps/api/**/models.py", recursive=True) + glob.glob(
        "apps/api/**/models_ext.py", recursive=True
    )

    for filepath in files:
        with open(filepath) as f:
            content = f.read()

        original = content

        # Ensure Uuid is imported
        if "String" in content and "Uuid" not in content:
            content = re.sub(
                r"from sqlalchemy import (.*?)(String)(.*)",
                r"from sqlalchemy import \1\2, Uuid\3",
                content,
            )

        # Replace String(36) with Uuid(as_uuid=False)
        content = content.replace("String(36)", "Uuid(as_uuid=False)")

        # Add ForeignKey to TenantApiKey's tenant_id if not present
        if "TenantApiKey" in content:
            if "ForeignKey" not in content:
                content = re.sub(
                    r"from sqlalchemy import (.*?)(Uuid)(.*)",
                    r"from sqlalchemy import \1\2, ForeignKey\3",
                    content,
                )
            content = re.sub(
                r"(tenant_id: Mapped\[str\] = mapped_column\()Uuid\(as_uuid=False\), (nullable=False, index=True\))",
                r'\1Uuid(as_uuid=False), ForeignKey("tenants.id", ondelete="CASCADE"), \2',
                content,
            )

        # Add ondelete="CASCADE" to existing ForeignKeys in conversation/models.py
        if "Conversation" in content or "Message" in content:
            content = content.replace(
                'ForeignKey("tenants.id")', 'ForeignKey("tenants.id", ondelete="CASCADE")'
            )
            content = content.replace(
                'ForeignKey("conversations.id")',
                'ForeignKey("conversations.id", ondelete="CASCADE")',
            )

        if content != original:
            with open(filepath, "w") as f:
                f.write(content)
            print(f"Updated {filepath}")


if __name__ == "__main__":
    refactor_models()
