import json
import requests
import boto3
from datetime import datetime
def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.client("dynamodb")
    terms = ["Indian", "Korean", "Chinese", "Italian", "Thai"]
    for term in terms:
        for offset in range(0,951,50):
            result = requests.get("https://api.yelp.com/v3/businesses/search",params={"term":term, "location":"Manhattan", "limit":50, "offset": offset}, headers={"Authorization":"Bearer <Access_Key>"})
            print(result)
            result = json.loads(result.text)
            for res in result["businesses"]:
                location = ""
                phone = ""
                cuisines = ""
                latitude = ""
                longitude = ""
                num_reviews = ""
                rating = ""
                zipcode = ""
                id = res["id"]
                name = res["name"]
                cuisines = ""
                for i in res["categories"]:
                    if i["title"] in terms:
                        cuisines = i["title"]
                if res["location"]["address1"]:
                    location = res["location"]["address1"]
                if res["location"]["zip_code"]:
                    zipcode = res["location"]["zip_code"]
                if res["review_count"]:
                    num_reviews = res["review_count"]
                if res["rating"]:
                    rating = res["rating"]
                if res["coordinates"]["latitude"]:
                    latitude = res["coordinates"]["latitude"]
                if res["coordinates"]["longitude"]:
                    longitude = res["coordinates"]["longitude"]
                if res["phone"]:
                    phone = res["phone"]
                if len(cuisines) != 0:
                    dynamodb.put_item(TableName='yelp-restaurants', Item={'id':{'S':id},'insertedAtTimestamp': {'S': str(datetime.now())}, 'name':{'S':name}, 'cuisines':{'S':cuisines}, 'location':{'S':location}, 'phone':{'S':phone}, 'number_of_reviews':{'S':str(num_reviews)}, 'rating': {'S':str(rating)}, 'zipcode': {'S':str(zipcode)}, 'latitude': {'S':str(latitude)}, 'longitude': {'S':str(longitude)}})
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
