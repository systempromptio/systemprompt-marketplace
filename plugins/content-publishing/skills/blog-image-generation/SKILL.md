---
name: blog-image-generation
description: "Generate and edit blog featured images using the Google Gemini API via curl. Supports text-to-image generation and image editing with style guidelines optimised for social media."
version: "1.0.0"
git_hash: "0000000"
---

# Blog Image Generation via Gemini API

Generate striking blog featured images using the Google Gemini API. Supports text-to-image generation and editing existing images.

## Prerequisites

- `GEMINI_API_KEY` stored as an encrypted plugin secret
- `jq` installed for JSON parsing
- `base64` available for decoding

### Retrieving the API Key

Use the `get_secrets` MCP tool from the `skill-manager` server to retrieve the decrypted `GEMINI_API_KEY` at runtime:

```
Tool: get_secrets
```

This returns the decrypted secret values for the current plugin. Extract `GEMINI_API_KEY` from the response and export it:

```bash
export GEMINI_API_KEY="<value from get_secrets>"
```

To set the secret for the first time, use the `manage_secrets` MCP tool:

```
Tool: manage_secrets
Parameters: action: "set", var_name: "GEMINI_API_KEY", var_value: "AIza...", is_secret: true
```

**Authentication method:** Pass the key as a query parameter (`?key=`), not as a header. The `x-goog-api-key` header is silently stripped by some proxies and environments.

## Text-to-Image Generation

Generate a new image from a text prompt:

```bash
PROMPT="Your image description here. CRITICAL: No text, words, letters, or numbers in the image."
SLUG="article-slug"
OUTPUT_DIR="/var/www/html/systemprompt-web/storage/files/images/blog"

RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [{\"text\": \"$PROMPT\"}]
    }],
    \"generationConfig\": {
      \"responseModalities\": [\"TEXT\", \"IMAGE\"]
    }
  }")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "API Error:"
  echo "$RESPONSE" | jq '.error'
  exit 1
fi

# Extract and save image
IMAGE_BASE64=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data')

if [ -n "$IMAGE_BASE64" ] && [ "$IMAGE_BASE64" != "null" ]; then
  mkdir -p "$OUTPUT_DIR"
  echo "$IMAGE_BASE64" | base64 -d > "$OUTPUT_DIR/$SLUG.png"
  echo "Image saved to $OUTPUT_DIR/$SLUG.png"
else
  echo "No image in response"
  echo "$RESPONSE" | jq .
fi
```

## Image Editing

Edit an existing image with text instructions:

```bash
INPUT_IMAGE="/var/www/html/systemprompt-web/storage/files/images/blog/existing.png"
EDIT_PROMPT="Replace the background with a dramatic sunset sky. CRITICAL: No text, words, letters, or numbers in the image."
SLUG="edited-slug"
OUTPUT_DIR="/var/www/html/systemprompt-web/storage/files/images/blog"

IMG_BASE64=$(base64 -w0 "$INPUT_IMAGE")
MIME_TYPE="image/png"

RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [
        {\"text\": \"$EDIT_PROMPT\"},
        {\"inline_data\": {\"mime_type\": \"$MIME_TYPE\", \"data\": \"$IMG_BASE64\"}}
      ]
    }],
    \"generationConfig\": {
      \"responseModalities\": [\"TEXT\", \"IMAGE\"]
    }
  }")

IMAGE_BASE64=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data')

if [ -n "$IMAGE_BASE64" ] && [ "$IMAGE_BASE64" != "null" ]; then
  mkdir -p "$OUTPUT_DIR"
  echo "$IMAGE_BASE64" | base64 -d > "$OUTPUT_DIR/$SLUG.png"
  echo "Edited image saved to $OUTPUT_DIR/$SLUG.png"
else
  echo "Error or no image in response"
  echo "$RESPONSE" | jq '.error // .'
fi
```

## Configuration Options

### Aspect Ratios

Add `imageConfig` to `generationConfig` for custom dimensions:

```json
"generationConfig": {
  "responseModalities": ["TEXT", "IMAGE"],
  "imageConfig": {
    "aspectRatio": "16:9"
  }
}
```

| Aspect Ratio | Use Case |
|-------------|----------|
| `1:1` | Square (Instagram, profile images) |
| `3:4` | Portrait |
| `4:3` | Landscape (default) |
| `9:16` | Vertical (Stories, mobile) |
| `16:9` | Widescreen (blog featured, OpenGraph) |

### Available Models

| Model | Notes |
|-------|-------|
| `gemini-2.5-flash-image` | **Recommended** (Nano Banana). Production-ready, ~$0.039/image |
| `gemini-3.1-flash-image-preview` | Latest preview (Nano Banana 2). Fastest, optimised for high volume |
| `gemini-3-pro-image-preview` | Premium quality. Higher cost, advanced creative capabilities |

To use a different model, replace the model name in the endpoint URL.

## Style Guidelines

### Critical Rules

1. **NEVER include text in images** - No words, letters, numbers, or symbols. AI models struggle with text and it looks unprofessional.
2. **Optimise for social impact** - Bold, attention-grabbing visuals that stop the scroll.
3. **Creative and satirical** - Editorial illustration meets modern meme culture. Think New Yorker cartoons, political satire, visual metaphors.

### What Works

- Visual metaphors (house of cards for fragile systems, puppet strings for control)
- Satirical takes on tech culture (developer stereotypes, startup tropes)
- Abstract representations of technical concepts
- Dramatic lighting and composition
- Unexpected juxtapositions
- Bold compositions with strong visual hierarchy
- High contrast (works as thumbnails in dark/light mode)

### What to Avoid

- Generic stock photo aesthetics
- Literal representations (showing actual code, laptops)
- Busy compositions that don't thumbnail well
- Safe, corporate, forgettable imagery
- Any text, labels, or captions in the image

## Prompt Structure

When crafting image generation prompts:

```
[Visual concept/metaphor] for blog post about [topic].
Style: [specific artistic direction].
CRITICAL: No text, words, letters, or numbers in the image.
Mood: [emotional tone].
Composition: [framing guidance].
```

## Examples

**Topic:** AI agents failing in production
**Prompt:** A gleaming robot in a suit confidently walking off a cliff edge, other robots following behind. Editorial illustration style, dramatic perspective looking up at the cliff. CRITICAL: No text, words, letters, or numbers in the image. Mood: darkly humorous, cautionary. Bold colours, stark shadows.

**Topic:** Cost optimisation in AI
**Prompt:** A person carefully balancing on a tightrope made of dollar bills stretched between two cloud formations, with gold coins raining down. Satirical New Yorker cartoon style. CRITICAL: No text, words, letters, or numbers in the image. Mood: precarious but determined. Clean composition with strong central focus.

**Topic:** God agents vs modular architecture
**Prompt:** A massive octopus with tangled tentacles trying to do everything at once, while nearby a coordinated school of small fish moves efficiently in formation. Surrealist editorial style. CRITICAL: No text, words, letters, or numbers in the image. Mood: chaotic vs elegant contrast. Split composition showing both approaches.

## Rate Limits

| Tier | Images Per Minute |
|------|-------------------|
| Free | 2 IPM |
| Tier 1 | 10 IPM |
| Tier 2 | 20 IPM |

If you receive a 429 error, wait and retry. The free tier is very limited.

## Output

Save images to: `/var/www/html/systemprompt-web/storage/files/images/blog/{slug}.png`

Reference in blog frontmatter as: `image: "/files/images/blog/{slug}.png"`
