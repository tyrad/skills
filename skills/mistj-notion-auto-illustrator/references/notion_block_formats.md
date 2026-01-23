# Notion Image Block Formats

To insert an image into Notion via the MCP `patch-block-children` tool, use the following JSON structure for the `children` array:

### External Image (UpYun URL)

```json
[
  {
    "object": "block",
    "type": "image",
    "image": {
      "type": "external",
      "external": {
        "url": "https://your-bucket.b0.upaiyun.com/path/to/image.png"
      }
    }
  }
]
```

### With Caption

```json
[
  {
    "object": "block",
    "type": "image",
    "image": {
      "type": "external",
      "external": {
        "url": "https://your-bucket.b0.upaiyun.com/path/to/image.png"
      },
      "caption": [
        {
          "type": "text",
          "text": {
            "content": "Illustration: The concept of modular blocks in Notion"
          }
        }
      ]
    }
  }
]
```

### Usage with MCP

When calling `patch-block-children`:

- `block_id`: The ID of the page (or parent container).
- `after`: The ID of the block you want the image to appear _after_.
- `children`: The array defined above.
