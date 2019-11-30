import boto3, json
from boto3.dynamodb.conditions import Key, Attr

class EntityController:

    def __init__(self, table_name, primary_key, sort_key=None):
        self.TABLE_NAME = table_name
        self.PRIMARY_KEY = primary_key
        self.SORT_KEY = sort_key
    
        # Get the service resource.
        self.dynamodb = boto3.resource('dynamodb')

        #Create a client to interact with DynamoDb
        self.dynamo_client = boto3.client('dynamodb')

        #Check if the table exists. Otherwise create a new table.
        existing_tables = self.dynamo_client.list_tables()['TableNames']

        if table_name not in existing_tables:
            self.create_table()
        else:
            #Lazy load the table
            self.table = self.dynamodb.Table(self.TABLE_NAME) 

        
    