from app.models.community import CommunityPostCreate
from pydantic import ValidationError

def test_payload(name, payload):
    print(f"\n--- Testing {name} ---")
    try:
        m = CommunityPostCreate(**payload)
        print(f"SUCCESS: {m}")
    except ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

# Perfect payload
test_payload("Valid Payload", {
    "title": "A Great Title for Testing",
    "content": "This is a content that is longer than ten characters.",
    "category": "discussion",
    "images": []
})

# Missing category
test_payload("Missing Category", {
    "title": "A Great Title for Testing",
    "content": "This is a content that is longer than ten characters.",
    "images": []
})

# Short title
test_payload("Short Title", {
    "title": "abc",
    "content": "This is a content that is longer than ten characters.",
    "category": "discussion",
    "images": []
})

# Missing images
test_payload("Missing Images (Should default)", {
    "title": "A Great Title for Testing",
    "content": "This is a content that is longer than ten characters.",
    "category": "discussion"
})
