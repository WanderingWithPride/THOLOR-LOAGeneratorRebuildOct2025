# Digital Signatures for LOA Documents

## Overview

The LOR/LOA Generator now includes **automatic digital signature generation** for all authorized signatories on LOA documents!

## How It Works

When an LOA is generated, the system automatically:
1. Detects which signatory was selected (Sarah, Michael, or Maureen)
2. Generates a professional digital signature image
3. Embeds the signature in the LOA document
4. Adds the signatory's name and title below

## Signature Styles

Signatures are generated in a **script-style font** that mimics handwritten signatures, similar to Adobe Acrobat's signature feature.

### Current Signatories

#### 1. Sarah Louden
- **Title**: Founder and Executive Director
- **Email**: sarah@totalhealthconferencing.com
- **Signature**: Uses existing `sarah_signature.jpg` if available, or generates digital signature

#### 2. Maureen Louden
- **Full Name**: Maureen Louden (Previously Schnepf)
- **Title**: Director, Sales and Operations
- **Email**: maureen@totalhealthoncology.com
- **Signature**: Auto-generated digital signature

#### 3. Michael Eisinger, MA
- **Title**: Manager, Business Operations
- **Email**: michael@totalhealthoncology.com
- **Phone**: (202) 834-3330
- **Signature**: Auto-generated digital signature

## Signature Generation

The system uses the `core/signature_generator.py` module to:
- Create signature images on-the-fly
- Use script/cursive fonts when available
- Fall back to elegant fonts if script fonts aren't available
- Generate 400x100 pixel signatures in navy blue (#000080)

## Usage

When generating an LOA:
1. Select document type: **LOA**
2. Choose signatory from dropdown (Sarah, Michael, or Maureen)
3. Fill in all other details
4. Click **Generate Documents**

The LOA will automatically include the selected person's digital signature!

## File Locations

**Signature Generator**: `core/signature_generator.py`
**Settings**: `config/settings.py` (contains all signatory information)
**Assets**: `assets/` (stores signature images)

## Benefits

✅ **Professional Appearance** - LOAs look signed and official
✅ **No Manual Signing** - Signatures appear automatically
✅ **Consistent Branding** - All signatures match in style
✅ **Flexible** - Easy to add new signatories
✅ **Secure** - Signatures are generated per document

## Technical Details

**Font**: Script/cursive style (Brush Script MT, Lucida Handwriting, etc.)
**Color**: Navy blue (#000080) for professional appearance
**Size**: 2.0 inches wide in documents
**Format**: PNG with transparent background
**Generation**: On-demand, no storage needed (except optional cache)

## Future Enhancements

- Custom signature styles per person
- Upload your own signature images
- Signature position customization
- Multiple signature formats (script, print, etc.)

---

**Built for Total Health Conferencing** - Professional document generation with authentic-looking signatures!
