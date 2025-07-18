import json
import os
from pymongo import MongoClient
from bson.json_util import dumps

MONGO_URI = os.environ['MONGO_URI']
DATABASE_NAME = os.environ['DATABASE_NAME']

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db["Items"]

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def parse_request_body(event):
    try:
        if event.get('body'):
            return json.loads(event['body'])
        return {}
    except json.JSONDecodeError:
        return None

def lambda_handler_get_hello(event, context):
    return create_response(200, "Hello, World!")

def lambda_handler_get_item(event, context):
    try:
        item_id = event['pathParameters']['id']
        item = collection.find_one({"id": item_id})
        
        if item:
            return create_response(200, json.loads(dumps(item)))
        else:
            return create_response(404, {"error": f"Item with id {item_id} not found"})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

def lambda_handler_post_create_item(event, context):
    try:
        data = parse_request_body(event)
        if data is None:
            return create_response(400, {"error": "Invalid JSON in request body"})
        
        item_id = data.get("id")
        if not item_id:
            return create_response(400, {"error": "Missing 'id' in request"})
        
        if collection.find_one({"id": item_id}):
            return create_response(409, {"error": f"Item with id '{item_id}' already exists."})
        
        collection.insert_one(data)
        return create_response(201, {"success": f"Item with id '{item_id}' created."})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

def lambda_handler_put_add_batter(event, context):
    try:
        item_id = event['pathParameters']['id']
        data = parse_request_body(event)
        
        if data is None:
            return create_response(400, {"error": "Invalid JSON in request body"})
        
        batter_id = str(data.get('id'))
        batter_type = data.get('type')
        
        if not batter_id or not batter_type:
            return create_response(400, {"error": "Missing 'id' or 'type' in request"})
        
        item = collection.find_one({"id": item_id})
        if not item:
            return create_response(404, {"error": f"Item with id '{item_id}' not found."})
        
        batters_list = item.get("batters", {}).get("batter", [])
        if any(batter.get("id") == batter_id for batter in batters_list):
            return create_response(409, {"error": f"Batter with id '{batter_id}' already exists."})
        
        batters_list.append({"id": batter_id, "type": batter_type})
        updated_batters = {"batters.batter": batters_list}
        
        collection.update_one({"id": item_id}, {"$set": updated_batters})
        
        return create_response(200, {"success": f"Batter with id '{batter_id}' added to item '{item_id}'."})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

def lambda_handler_delete_item(event, context):
    try:
        item_id = event['pathParameters']['id']
        result = collection.delete_one({"id": item_id})
        
        if result.deleted_count == 1:
            return create_response(200, {"success": f"Item with id '{item_id}' has been deleted."})
        else:
            return create_response(404, {"error": f"Item with id '{item_id}' not found."})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

def lambda_handler_delete_batter(event, context):
    try:
        item_id = event['pathParameters']['id']
        data = parse_request_body(event)
        
        if data is None:
            return create_response(400, {"error": "Invalid JSON in request body"})
        
        batter_id = str(data.get("id"))
        if not batter_id:
            return create_response(400, {"error": "Missing 'id' of batter to delete"})
        
        item = collection.find_one({"id": item_id})
        if not item:
            return create_response(404, {"error": f"Item with id '{item_id}' not found."})
        
        batters = item.get("batters", {}).get("batter", [])
        new_batters = [b for b in batters if b.get("id") != batter_id]
        
        if len(batters) == len(new_batters):
            return create_response(404, {"error": f"No batter with id '{batter_id}' found."})
        
        collection.update_one({"id": item_id}, {"$set": {"batters.batter": new_batters}})
        
        return create_response(200, {"success": f"Batter with id '{batter_id}' removed from item '{item_id}'."})
    
    except Exception as e:
        return create_response(500, {"error": str(e)})

def lambda_handler_router(event, context):
    http_method = event.get('httpMethod', '').upper()
    resource_path = event.get('resource', '')
    
    routes = {
        ('GET', '/api/hello'): lambda_handler_get_hello,
        ('GET', '/api/item/{id}'): lambda_handler_get_item,
        ('POST', '/api/item/create'): lambda_handler_post_create_item,
        ('PUT', '/api/item/{id}'): lambda_handler_put_add_batter,
        ('DELETE', '/api/item/{id}'): lambda_handler_delete_item,
        ('DELETE', '/api/item/{id}/batter'): lambda_handler_delete_batter,
    }
    
    route_key = (http_method, resource_path)
    
    if route_key in routes:
        return routes[route_key](event, context)
    else:
        return create_response(404, {"error": "Route not found"})