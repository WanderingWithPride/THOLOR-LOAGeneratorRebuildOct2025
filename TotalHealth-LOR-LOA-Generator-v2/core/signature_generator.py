"""
Digital Signature Generator - Total Health Conferencing
Creates Adobe Acrobat-style digital signatures for LOA documents
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path
from typing import Optional
import os


class SignatureGenerator:
    """
    Generates digital signature images that look like Adobe Acrobat signatures

    Creates signature-style text with script-like font for professional appearance
    """

    @staticmethod
    def generate_signature(
        name: str,
        width: int = 400,
        height: int = 100,
        font_size: int = 48,
        color: str = "#000080"
    ) -> BytesIO:
        """
        Generate a signature-style image from a name

        Args:
            name: Full name to convert to signature
            width: Image width in pixels
            height: Image height in pixels
            font_size: Font size for signature
            color: Signature color (default navy blue)

        Returns:
            BytesIO object containing PNG signature image
        """
        # Create transparent image
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Try to use a script-like font, fall back to default if not available
        font = SignatureGenerator._get_signature_font(font_size)

        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw the signature text in italic style
        draw.text((x, y), name, font=font, fill=color)

        # Add slight underline for signature effect (optional)
        # underline_y = y + text_height + 5
        # draw.line([(x, underline_y), (x + text_width, underline_y)], fill=color, width=2)

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer

    @staticmethod
    def _get_signature_font(size: int):
        """
        Get the best available signature-style font

        Tries cursive/script fonts, falls back to bold italic
        """
        # List of preferred signature-style fonts (in order of preference)
        preferred_fonts = [
            'Brush Script MT',
            'Lucida Handwriting',
            'Segoe Script',
            'Comic Sans MS',  # Not ideal but better than nothing
        ]

        # Try each preferred font
        for font_name in preferred_fonts:
            try:
                return ImageFont.truetype(font_name, size)
            except (OSError, IOError):
                continue

        # Fall back to default font
        try:
            return ImageFont.load_default()
        except:
            return None

    @staticmethod
    def generate_all_signatures(output_dir: Path = None):
        """
        Generate signature images for all signatories

        Args:
            output_dir: Directory to save signatures (default: assets/)
        """
        from config.settings import SARAH_INFO, MICHAEL_INFO, MAUREEN_INFO, ASSETS_DIR

        if output_dir is None:
            output_dir = ASSETS_DIR

        output_dir.mkdir(exist_ok=True)

        # Generate signatures for each person
        signatories = {
            'sarah': SARAH_INFO['name'],
            'michael': f"{MICHAEL_INFO['name']}, {MICHAEL_INFO['credentials']}",
            'maureen': MAUREEN_INFO['name']
        }

        for key, name in signatories.items():
            # Skip Sarah if she already has a signature
            if key == 'sarah' and (output_dir / 'sarah_signature.jpg').exists():
                print(f"✓ Sarah's signature already exists, skipping")
                continue

            signature_buffer = SignatureGenerator.generate_signature(
                name=name,
                width=400,
                height=100,
                font_size=48,
                color="#000080"  # Navy blue for professional look
            )

            # Save to file
            output_path = output_dir / f'{key}_signature_generated.png'
            with open(output_path, 'wb') as f:
                f.write(signature_buffer.getvalue())

            print(f"✓ Generated signature for {name} -> {output_path}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_signature_for_person(person_key: str) -> Optional[BytesIO]:
    """
    Get signature image for a specific person

    Args:
        person_key: 'sarah', 'michael', or 'maureen'

    Returns:
        BytesIO with signature image, or None if not found
    """
    from config.settings import SARAH_INFO, MICHAEL_INFO, MAUREEN_INFO, ASSETS_DIR

    # Map person to their info
    person_map = {
        'sarah': SARAH_INFO['name'],
        'michael': f"{MICHAEL_INFO['name']}, {MICHAEL_INFO['credentials']}",
        'maureen': MAUREEN_INFO['name']
    }

    if person_key not in person_map:
        return None

    # Check for existing signature files first
    signature_files = [
        ASSETS_DIR / f'{person_key}_signature.jpg',
        ASSETS_DIR / f'{person_key}_signature.png',
        ASSETS_DIR / f'{person_key}_signature_generated.png',
    ]

    for sig_file in signature_files:
        if sig_file.exists():
            with open(sig_file, 'rb') as f:
                buffer = BytesIO(f.read())
                buffer.seek(0)
                return buffer

    # If no file exists, generate one on the fly
    return SignatureGenerator.generate_signature(person_map[person_key])


def has_signature_file(person_key: str) -> bool:
    """
    Check if a signature file exists for a person

    Args:
        person_key: 'sarah', 'michael', or 'maureen'

    Returns:
        True if signature file exists
    """
    from config.settings import ASSETS_DIR

    signature_files = [
        ASSETS_DIR / f'{person_key}_signature.jpg',
        ASSETS_DIR / f'{person_key}_signature.png',
        ASSETS_DIR / f'{person_key}_signature_generated.png',
    ]

    return any(sig_file.exists() for sig_file in signature_files)
