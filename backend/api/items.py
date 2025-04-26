from datetime import datetime
import uuid

# In-memory database for demo
ITEMS_DB = {}

def get_items():
    """
    Get all items from the database
    """
    return list(ITEMS_DB.values())

def create_item(body):
    """
    Create a new item
    """
    item_id = len(ITEMS_DB) + 1
    new_item = {
        "id": item_id,
        "title": body.get("title"),
        "description": body.get("description", ""),
        "completed": body.get("completed", False),
        "createdAt": datetime.now().isoformat()
    }
    ITEMS_DB[item_id] = new_item
    return new_item, 201

def get_item_by_id(itemId):
    """
    Get a specific item by ID
    """
    item = ITEMS_DB.get(itemId)
    if item:
        return item
    return {"error": "Item not found"}, 404

def update_item(itemId, body):
    """
    Update an existing item
    """
    if itemId not in ITEMS_DB:
        return {"error": "Item not found"}, 404
    
    item = ITEMS_DB[itemId]
    item["title"] = body.get("title", item["title"])
    item["description"] = body.get("description", item["description"])
    item["completed"] = body.get("completed", item["completed"])
    
    return item

def delete_item(itemId):
    """
    Delete an item
    """
    if itemId not in ITEMS_DB:
        return {"error": "Item not found"}, 404
    
    del ITEMS_DB[itemId]
    return None, 204 