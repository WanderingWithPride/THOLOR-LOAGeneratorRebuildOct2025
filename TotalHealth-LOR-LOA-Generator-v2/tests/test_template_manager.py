"""
Tests for Template Manager - Total Health Conferencing
Tests template CRUD operations and rendering
"""
import pytest
from pathlib import Path
import tempfile
import shutil

from services.template_manager import (
    TemplateManager,
    DocumentTemplate,
    get_template_manager
)


@pytest.fixture
def temp_templates_dir():
    """Create temporary templates directory"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def template_manager(temp_templates_dir):
    """Create template manager with temp directory"""
    return TemplateManager(temp_templates_dir)


class TestDocumentTemplate:
    """Test DocumentTemplate class"""

    def test_template_creation(self):
        """Test creating a template"""
        template = DocumentTemplate(
            template_id="test_template",
            name="Test Template",
            document_type="LOR",
            content="Dear {company_name}, Event: {meeting_name}",
            variables=["company_name", "meeting_name"],
            description="Test template"
        )

        assert template.template_id == "test_template"
        assert template.name == "Test Template"
        assert template.document_type == "LOR"

    def test_template_rendering(self):
        """Test rendering template with context"""
        template = DocumentTemplate(
            template_id="test",
            name="Test",
            document_type="LOR",
            content="Dear {company_name}, Event: {meeting_name}",
            variables=["company_name", "meeting_name"]
        )

        context = {
            "company_name": "Acme Corp",
            "meeting_name": "ASCO 2025"
        }

        rendered = template.render(context)

        assert "Dear Acme Corp" in rendered
        assert "Event: ASCO 2025" in rendered

    def test_template_serialization(self):
        """Test converting template to/from dict"""
        template = DocumentTemplate(
            template_id="test",
            name="Test",
            document_type="LOR",
            content="Test content",
            variables=["var1", "var2"]
        )

        # To dict
        data = template.to_dict()
        assert data['template_id'] == "test"
        assert data['name'] == "Test"

        # From dict
        template2 = DocumentTemplate.from_dict(data)
        assert template2.template_id == template.template_id
        assert template2.content == template.content


class TestTemplateManager:
    """Test TemplateManager class"""

    def test_default_templates_created(self, template_manager):
        """Test that default templates are created"""
        # Default templates should be created on init
        lor_template = template_manager.get_template("default_lor")
        loa_template = template_manager.get_template("default_loa")

        assert lor_template is not None
        assert loa_template is not None
        assert lor_template.is_default
        assert loa_template.is_default

    def test_save_and_get_template(self, template_manager):
        """Test saving and retrieving a template"""
        template = DocumentTemplate(
            template_id="custom_template",
            name="Custom Template",
            document_type="LOR",
            content="Custom content: {company_name}",
            variables=["company_name"]
        )

        template_manager.save_template(template)

        # Retrieve it
        retrieved = template_manager.get_template("custom_template")

        assert retrieved is not None
        assert retrieved.name == "Custom Template"
        assert retrieved.content == "Custom content: {company_name}"

    def test_list_templates(self, template_manager):
        """Test listing all templates"""
        # Should have 2 default templates
        all_templates = template_manager.list_templates()
        assert len(all_templates) >= 2

        # Filter by type
        lor_templates = template_manager.list_templates(document_type="LOR")
        assert len(lor_templates) >= 1

        loa_templates = template_manager.list_templates(document_type="LOA")
        assert len(loa_templates) >= 1

    def test_create_template(self, template_manager):
        """Test creating a new template"""
        template = template_manager.create_template(
            name="My Custom Template",
            document_type="LOA",
            content="Agreement for {company_name} at {venue}",
            description="Custom LOA template"
        )

        assert template is not None
        assert template.name == "My Custom Template"
        assert "company_name" in template.variables
        assert "venue" in template.variables

    def test_delete_template(self, template_manager):
        """Test deleting a template"""
        # Create a custom template
        template = DocumentTemplate(
            template_id="deletable",
            name="Deletable",
            document_type="LOR",
            content="Test",
            variables=[]
        )

        template_manager.save_template(template)

        # Delete it
        success = template_manager.delete_template("deletable")
        assert success

        # Verify deletion
        retrieved = template_manager.get_template("deletable")
        assert retrieved is None

    def test_cannot_delete_default_template(self, template_manager):
        """Test that default templates cannot be deleted"""
        success = template_manager.delete_template("default_lor")
        assert not success

        # Verify it still exists
        template = template_manager.get_template("default_lor")
        assert template is not None

    def test_get_default_template(self, template_manager):
        """Test getting default template by type"""
        lor_default = template_manager.get_default_template("LOR")
        assert lor_default is not None
        assert lor_default.document_type == "LOR"

        loa_default = template_manager.get_default_template("LOA")
        assert loa_default is not None
        assert loa_default.document_type == "LOA"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
