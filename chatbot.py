import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    text = event.get("data")
    client = boto3.client('lex-runtime')
    response=client.post_text(
        botName='DiningBot',
        botAlias='DiningBot',
        userId='test',
        inputText=text
    )
    return {
        'statusCode': 200,
        'headers':{
            "x-custom-header":"my custom header value",
            "Access-Control-Allow-Origin":"*",
            "Access-Control-Allow-Methods":"POST,GET",
            "Access-Control-Allow-Headers":"x-api-key"
        },
        'body': json.dumps(response.get("message")),
        # 'body':json.dumps('hhhh'),
        'event':event
    }
