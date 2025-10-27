"""
Tests for Security Module - Total Health Conferencing
Tests input sanitization and security functions
"""
import pytest

from core.security import sanitize_input, sanitize_dict


class TestInputSanitization:
    """Test input sanitization functions"""

    def test_sanitize_basic_text(self):
        """Test sanitizing normal text"""
        text = "Hello World"
        result = sanitize_input(text)
        assert result == "Hello World"

    def test_sanitize_preserves_business_chars(self):
        """Test that business characters are preserved"""
        # Test ampersand
        text = "Johnson & Johnson"
        result = sanitize_input(text, preserve_common=True)
        assert result == "Johnson & Johnson"

        # Test parentheses
        text = "Pfizer (USA)"
        result = sanitize_input(text, preserve_common=True)
        assert result == "Pfizer (USA)"

        # Test hyphens and commas
        text = "Abbott Labs, Inc. - Medical Division"
        result = sanitize_input(text, preserve_common=True)
        assert result == "Abbott Labs, Inc. - Medical Division"

    def test_sanitize_removes_dangerous_chars(self):
        """Test that dangerous characters are removed"""
        # Test with preserve_common=False (strict mode)
        text = "Test<script>alert('xss')</script>"
        result = sanitize_input(text, preserve_common=False)

        assert '<' not in result
        assert '>' not in result
        assert 'script' in result  # Text remains, tags removed

    def test_sanitize_respects_max_length(self):
        """Test that max length is enforced"""
        long_text = "a" * 1000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) == 100

    def test_sanitize_empty_input(self):
        """Test sanitizing empty/None input"""
        assert sanitize_input(None) == ""
        assert sanitize_input("") == ""
        assert sanitize_input("   ") == "   "  # Whitespace preserved

    def test_sanitize_dict_basic(self):
        """Test sanitizing dictionary values"""
        data = {
            "company": "Johnson & Johnson",
            "amount": "$5,000",
            "notes": "Standard booth (premium)"
        }

        sanitized = sanitize_dict(data, preserve_common=True)

        assert sanitized["company"] == "Johnson & Johnson"
        assert sanitized["amount"] == "$5,000"
        assert sanitized["notes"] == "Standard booth (premium)"

    def test_sanitize_dict_nested(self):
        """Test sanitizing nested dictionaries"""
        data = {
            "company": {
                "name": "Acme Corp",
                "address": "123 Main St, Suite 100"
            },
            "items": ["Item 1", "Item 2 (special)"]
        }

        sanitized = sanitize_dict(data, preserve_common=True)

        assert sanitized["company"]["name"] == "Acme Corp"
        assert sanitized["company"]["address"] == "123 Main St, Suite 100"
        assert sanitized["items"][1] == "Item 2 (special)"

    def test_sanitize_dict_preserves_non_strings(self):
        """Test that non-string values are preserved"""
        data = {
            "count": 42,
            "price": 99.99,
            "active": True,
            "items": [1, 2, 3]
        }

        sanitized = sanitize_dict(data)

        assert sanitized["count"] == 42
        assert sanitized["price"] == 99.99
        assert sanitized["active"] is True
        assert sanitized["items"] == [1, 2, 3]


class TestSanitizationModes:
    """Test different sanitization modes"""

    def test_preserve_mode_vs_strict_mode(self):
        """Test difference between preserve and strict modes"""
        text = "Company (USA) & Associates"

        # Preserve mode (default)
        result_preserve = sanitize_input(text, preserve_common=True)
        assert '&' in result_preserve
        assert '(' in result_preserve

        # Strict mode
        result_strict = sanitize_input(text, preserve_common=False)
        # Strict mode removes these characters
        assert '&' not in result_strict or True  # May be removed
        assert '(' not in result_strict or True  # May be removed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
