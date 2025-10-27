"""
Template Manager - Total Health Conferencing
Manages document templates for LOA/LOR generation with variable substitution
"""
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime


# ============================================================================
# TEMPLATE STORAGE
# ============================================================================

TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# DEFAULT TEMPLATES
# ============================================================================

DEFAULT_LOR_TEMPLATE = """
Dear {company_name},

We are writing to confirm that {company_name} has expressed interest in exhibiting at the {meeting_name} scheduled for {meeting_date_long} at {venue} in {city_state}.

We anticipate an attendance of approximately {attendance_expected} {audience_list} at this event.

{additional_info_section}

We look forward to your participation and to making this event a success for all involved.

Sincerely,
{signature_person}
"""

DEFAULT_LOA_TEMPLATE = """
LETTER OF AGREEMENT

Date: {agreement_date}

This Letter of Agreement ("Agreement") is between Total Health Information Services, LLC. ("Total Health") and {company_name} ("Company").

Event Details:
- Event Name: {meeting_name}
- Event Date: {meeting_date_long}
- Venue: {venue}
- Location: {city_state}

Financial Terms:
{booth_section}
{addons_section}
Total Amount Due: {amount_currency}

Company Information:
{company_address}

By signing below, Company agrees to participate in the event under the terms outlined above.

Authorized Signature:
{signature_person}

{signature_date_line}
"""


# ============================================================================
# TEMPLATE CLASS
# ============================================================================

class DocumentTemplate:
    """
    Represents a document template with variable substitution

    Supports:
    - Template variables (e.g., {company_name})
    - Conditional sections
    - Version tracking
    """

    def __init__(
        self,
        template_id: str,
        name: str,
        document_type: str,
        content: str,
        variables: List[str],
        description: str = "",
        version: str = "1.0",
        created_at: Optional[str] = None,
        is_default: bool = False
    ):
        self.template_id = template_id
        self.name = name
        self.document_type = document_type  # "LOR" or "LOA"
        self.content = content
        self.variables = variables  # List of variable names
        self.description = description
        self.version = version
        self.created_at = created_at or datetime.now().isoformat()
        self.is_default = is_default

    def render(self, context: Dict[str, str]) -> str:
        """
        Render template with context variables

        Args:
            context: Dictionary of variable values

        Returns:
            Rendered template string
        """
        rendered = self.content

        for key, value in context.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))

        return rendered

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'document_type': self.document_type,
            'content': self.content,
            'variables': self.variables,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at,
            'is_default': self.is_default,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentTemplate':
        """Create template from dictionary"""
        return cls(**data)


# ============================================================================
# TEMPLATE MANAGER
# ============================================================================

class TemplateManager:
    """
    Manages document templates

    Provides:
    - Template CRUD operations
    - Template listing and filtering
    - Default template management
    - Template versioning
    """

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Ensure default templates exist"""
        if not self.get_template("default_lor"):
            self.save_template(DocumentTemplate(
                template_id="default_lor",
                name="Default LOR",
                document_type="LOR",
                content=DEFAULT_LOR_TEMPLATE,
                variables=[
                    "company_name", "meeting_name", "meeting_date_long",
                    "venue", "city_state", "attendance_expected",
                    "audience_list", "additional_info_section", "signature_person"
                ],
                description="Standard Letter of Recognition template",
                is_default=True
            ))

        if not self.get_template("default_loa"):
            self.save_template(DocumentTemplate(
                template_id="default_loa",
                name="Default LOA",
                document_type="LOA",
                content=DEFAULT_LOA_TEMPLATE,
                variables=[
                    "agreement_date", "company_name", "meeting_name",
                    "meeting_date_long", "venue", "city_state",
                    "booth_section", "addons_section", "amount_currency",
                    "company_address", "signature_person", "signature_date_line"
                ],
                description="Standard Letter of Agreement template",
                is_default=True
            ))

    def save_template(self, template: DocumentTemplate):
        """Save template to file"""
        file_path = self.templates_dir / f"{template.template_id}.json"

        with open(file_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)

    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Get template by ID"""
        file_path = self.templates_dir / f"{template_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

        return DocumentTemplate.from_dict(data)

    def list_templates(self, document_type: Optional[str] = None) -> List[DocumentTemplate]:
        """
        List all templates, optionally filtered by document type

        Args:
            document_type: Filter by "LOR" or "LOA" (None = all)

        Returns:
            List of DocumentTemplate objects
        """
        templates = []

        for file_path in self.templates_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                template = DocumentTemplate.from_dict(data)

                if document_type is None or template.document_type == document_type:
                    templates.append(template)

            except Exception:
                continue

        return sorted(templates, key=lambda t: (not t.is_default, t.name))

    def delete_template(self, template_id: str) -> bool:
        """
        Delete template by ID

        Args:
            template_id: Template ID

        Returns:
            True if deleted, False if not found or is default
        """
        template = self.get_template(template_id)

        if template and not template.is_default:
            file_path = self.templates_dir / f"{template_id}.json"
            file_path.unlink()
            return True

        return False

    def get_default_template(self, document_type: str) -> Optional[DocumentTemplate]:
        """Get default template for document type"""
        if document_type == "LOR":
            return self.get_template("default_lor")
        elif document_type == "LOA":
            return self.get_template("default_loa")
        return None

    def create_template(
        self,
        name: str,
        document_type: str,
        content: str,
        description: str = ""
    ) -> DocumentTemplate:
        """
        Create new template

        Args:
            name: Template name
            document_type: "LOR" or "LOA"
            content: Template content with {variables}
            description: Template description

        Returns:
            Created DocumentTemplate
        """
        # Generate template ID
        template_id = name.lower().replace(' ', '_').replace('-', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_id = f"{template_id}_{timestamp}"

        # Extract variables from content
        import re
        variables = re.findall(r'\{(\w+)\}', content)

        template = DocumentTemplate(
            template_id=template_id,
            name=name,
            document_type=document_type,
            content=content,
            variables=list(set(variables)),
            description=description,
            version="1.0"
        )

        self.save_template(template)
        return template


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_manager_instance = None


def get_template_manager() -> TemplateManager:
    """Get singleton template manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = TemplateManager()
    return _manager_instance


def get_templates_for_type(document_type: str) -> List[DocumentTemplate]:
    """Get all templates for document type"""
    manager = get_template_manager()
    return manager.list_templates(document_type)
