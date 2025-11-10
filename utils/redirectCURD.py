import json
import os
import aiofiles
import asyncio

async def load_json(file_path):
    """Helper function to load JSON file asynchronously."""
    if not os.path.exists(file_path):
        return {}
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
        if not content.strip():
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

async def save_json(file_path, data):
    """Helper function to save dictionary as JSON file asynchronously."""
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(data, indent=4))

async def update_json(file_path, key, value):
    """Update or add a key-value pair in a JSON file asynchronously."""
    data = await load_json(file_path)
    data[key] = value
    await save_json(file_path, data)
    print(f"✅ Updated key '{key}' with value '{value}'.")

async def get_value(file_path, key):
    """Get the value of a given key from a JSON file asynchronously."""
    data = await load_json(file_path)
    return data.get(key, False)

async def delete_key(file_path, key):
    """Delete a given key from a JSON file asynchronously."""
    data = await load_json(file_path)
    if key in data:
        del data[key]
        await save_json(file_path, data)
        # print(f"🗑️ Deleted key '{key}'.")
    else:
        print(f"Key '{key}' not found.")