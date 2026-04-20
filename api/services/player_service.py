import os
import boto3
from decimal import Decimal
from database.db import get_table
from dotenv import load_dotenv
load_dotenv()

from schemas.player_schema import PlayerProfileSchema, PlayerProfileUpdateSchema

from models.player_models import PlayerProfileModel


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
        return PlayerProfileSchema(**item)
    except Exception as e:
        print(f"Error loading player from DynamoDB: {e}")
    
    # TODO: add try catches to other methods later

# writes full game state to DynamoDB
def save_player(player_data: dict) -> None:
    """
    Saves (creates or overwrites) a player's game state.
    player_data must include player_name as the primary key.
    """
    # DynamoDB requires floats to be Decimal #TODO:
    table.put_item(Item=PlayerProfileModel(**player_data).to_decimals())

# partial update of specific fields
# ex: just trust + hunger after a care action
def update_player(player_name: str, updates: PlayerProfileUpdateSchema) -> PlayerProfileSchema:
    """
    Updates specific fields on a player record.
    Returns the full updated item.
    """
    fields = updates.model_dump(exclude_none=True)
    update_expr = 'SET ' + ', '.join(f'#{k} = :{k}' for k in fields)
    expr_names  = {f'#{k}': k for k in fields}
    expr_values = {f':{k}': Decimal(str(v)) if isinstance(v, float) else v
                   for k, v in fields.items()}

    response = table.update_item(
        Key={'player_name': player_name},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW',
    )
    return PlayerProfileSchema(**response['Attributes'])

# check if player exists
def player_exists(player_name: str) -> bool:
    """Returns True if player exists in DynamoDB."""
    return get_player(player_name) is not None