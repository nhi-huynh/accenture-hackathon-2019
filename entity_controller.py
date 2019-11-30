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

    def create_table(self, sample_data=None):
        """
        Create the DynamoDB table.
        """
        
        # Define key schema
        key_schema = []
        
        key_schema.append({
                            'AttributeName': self.PRIMARY_KEY,
                            'KeyType': 'HASH'
                        })

        # Define attribute definitions
        attribute_defs = [{
                            'AttributeName': self.PRIMARY_KEY,
                            'AttributeType': 'S'
                        }]

        if self.SORT_KEY:
            key_schema.append({
                    'AttributeName': self.SORT_KEY,
                    'KeyType': 'RANGE'
                })

            attribute_defs.append({
                    'AttributeName': self.SORT_KEY,
                    'AttributeType': 'S'
                })
        

        
        # Create the table based on the key schema and attribute definitions
        self.table = self.dynamodb.create_table(
            TableName=self.TABLE_NAME,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_defs,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Wait until the table exists.
        self.table.meta.client.get_waiter('table_exists').wait(TableName=self.TABLE_NAME)

        # Write some sample data to the table if the sample data is not None
        if sample_data:
            self.table.put_item(
                Item=sample_data
            # Item={
            #         "user_id": "U001",
            #         "first_name": "Nhi",
            #         "last_name": "Huynh",
            #         "email": "nhi.huynh@gmail.com",
            #         "password_hash": "password", 
            #         "account_id": "A001"
            #     }
            )

        # Print out some data about the table.
        print("Table " + self.TABLE_NAME + " has " + str(self.table.item_count) + " item count.")
        

    def get_entities(self):
        "Get all entities in the table"

        #Run a scan of the table name to return the entire table
        return self.dynamo_client.scan(
            TableName=self.TABLE_NAME
        )

    def query_entities(self, query):
        response = self.table.scan(
            FilterExpression=Attr(self.SORT_KEY).eq(query)
        )
        if 'Items' in response:
            return response['Items']
        else:
            return "No result found related to query " + query

    def get_entity(self, entity_id):
        """
        Get a entity by entity_id
        Parameter: 
            a string entity_id
        Return: 
            the entity that matches the given entity_id
        """

        response = self.table.get_item(
            Key={
                self.PRIMARY_KEY: entity_id,
            }
        )
        if 'Item' in response:
            entity = response['Item']
            return entity
        else:
            return "Object with key " + entity_id + " does not exist in the " + self.TABLE_NAME + " db."

    