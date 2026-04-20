import os
import boto3
from database.db import get_table, convert_decimals, convert_floats
from dotenv import load_dotenv
load_dotenv()

from schemas.player_schema import (
    AdopterProfileSchema, 
    StartGameSchema,
    PlayerProfileSchema
)

from models.player_models import (
    StartGameModel,
    AdopterProfileModel,
    PlayerProfileModel
)


dynamodb = boto3.resource("dynamodb")
ENV_MODE = os.getenv("ENV_MODE")
if(ENV_MODE == "local"):
    table = get_table()
else:
    table = dynamodb.Table(os.getenv("CONTACTFORMMESSAGES_TABLE_NAME"))


# fetches a player's full game state
def get_player(player_name: str) -> PlayerProfileSchema | None:
    """
    Fetches a player's game state from DynamoDB.
    Returns None if player doesn't exist.
    """
    try:
        response = table.get_item(
            Key={'player_name': player_name}
        )
        item = response.get('Item')
        if item is None:
            return None
        # DynamoDB stores numbers as Decimal — convert back to float/int, then validate with schema
        return PlayerProfileSchema(**convert_decimals(item))
    except Exception as e:
        print(f"Error loading player from DynamoDB: {e}")
    
    # TODO: add try catches to other methods later

# writes full game state to DynamoDB
def save_player(player_data: dict) -> None:
    """
    Saves (creates or overwrites) a player's game state.
    player_data must include player_name as the primary key.
    """
    # DynamoDB requires floats to be Decimal
    item = convert_floats(player_data)
    table.put_item(Item=item)

# partial update of specific fields
# ex: just trust + hunger after a care action
def update_player(player_name: str, updates: dict) -> dict:
    """
    Updates specific fields on a player record.
    Returns the full updated item.
    updates: dict of field names to new values
    """
    # build UpdateExpression dynamically from updates dict
    update_expr = 'SET ' + ', '.join(
        f'#{k} = :{k}' for k in updates
    )
    expr_names  = {f'#{k}': k for k in updates}
    expr_values = {f':{k}': convert_floats({k: v})[k]
                for k, v in updates.items()}

    response = table.update_item(
        Key={'player_name': player_name},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW',
    )
    return convert_decimals(response['Attributes'])

# check if player exists
def player_exists(player_name: str) -> bool:
    """Returns True if player exists in DynamoDB."""
    return get_player(player_name) is not None