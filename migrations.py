import uuid
import boto3
from trade.state import TradeState
from boto3.dynamodb.types import TypeSerializer
from typing import TypeVar, Generic

T = TypeVar("T")

dynamodb = boto3.client("dynamodb", endpoint_url="http://localhost:8000")


def get_table_id_field(data_schema: Generic[T]):
    attribute_definitions = None
    key_schema = None

    class_name = data_schema.__class__.__name__

    for k, v in data_schema.__dict__.items():
        if str(k).endswith("_id"):
            serializer = TypeSerializer()
            attribute_definitions = [
                {
                    "AttributeName": k,
                    "AttributeType": list(serializer.serialize(v).keys())[0],
                }
            ]
            key_schema = [{"AttributeName": k, "KeyType": "HASH"}]
            break

    if key_schema is None:
        raise NotImplementedError(
            f"Migration script expects one property name of the {class_name} class to end with '_id' to assume the role of primary key."
        )

    return attribute_definitions, key_schema


def create_table(data_class: Generic[T]):
    table_name = data_class.__class__.__name__ + "s"
    attribute_definitions, key_schema = get_table_id_field(data_class)

    response = dynamodb.create_table(
        AttributeDefinitions=attribute_definitions,
        TableName=table_name,
        KeySchema=key_schema,
        BillingMode="PROVISIONED",
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        Tags=[
            {"Key": "Application", "Value": "Investor Bot"},
        ],
        TableClass="STANDARD",
        DeletionProtectionEnabled=False,
        # ResourcePolicy="string",
    )

    return response


if __name__ == "__main__":
    state = TradeState(str(uuid.uuid4()), False, False, 1, 1, False, False)

    print(create_table(state))
