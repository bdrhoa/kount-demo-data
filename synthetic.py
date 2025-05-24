
import random
#import pandas as pd
from datetime import datetime
import uuid
import json
from faker import Faker

fake = Faker()

import csv
# Predefined real addresses (use known, valid addresses)



address_records = []
with open('equifax_locations.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        address_records.append({
            'street_address': row['Street Address'],
            'city': row['City'],
            'state_province': row['State/Province'],
            'postal_code': row['Postal Code'],
            'country_code': row['Country Code']
        })

def generate_record():
    order_id = uuid.uuid4().hex
    session_id = uuid.uuid4().hex
    now = datetime.utcnow().isoformat() + "Z"
    ip_address = fake.ipv4()

    address = random.choice(address_records)
    name = {
        "first": fake.first_name(),
        "middle": fake.first_name(),
        "family": fake.last_name(),
        "prefix": "Mr.",
        "suffix": "Jr."
    }
    person = {
        "name": name,
        "phoneNumber": fake.phone_number(),
        "emailAddress": fake.email(),
        "address": {
            "line1": address['street_address'],
            "line2": "Suite " + str(fake.random_int(100, 999)),
            "city": address['city'],
            "region": address['state_province'],
            "countryCode": address['country_code'],
            "postalCode": address['postal_code']
        }
    }

    item = {
        "id": uuid.uuid4().hex,
        "name": fake.word(),
        "description": fake.sentence(),
        "price": str(fake.random_int(100, 10000)),
        "quantity": fake.random_int(1, 5),
        "category": "Electronics",
        "subCategory": "Audio",
        "isDigital": False,
        "sku": uuid.uuid4().hex[:8],
        "brand": fake.company(),
        "url": fake.url(),
        "imageUrl": fake.image_url()
    }

    payment = {
        "type": "CREDIT_CARD",
        "paymentToken": fake.sha256(),
        "bin": str(fake.random_int(400000, 499999)),
        "last4": str(fake.random_int(1000, 9999))
    }

    transaction = {
        "processor": "ADYEN",
        "processorMerchantId": fake.credit_card_number(),
        "payment": payment,
        "subtotal": item["price"],
        "orderTotal": item["price"],
        "currency": "USD",
        "transactionStatus": "AUTHORIZED",
        "merchantTransactionId": uuid.uuid4().hex,
        "items": [{"id": item["id"], "quantity": item["quantity"]}]
    }

    fulfillment = {
        "type": "SHIPPED",
        "recipientPerson": person,
        "shipping": {
            "amount": "100",
            "provider": "FEDEX",
            "trackingNumber": "TRK" + uuid.uuid4().hex[:10],
            "method": "STANDARD"
        },
        "items": [{"id": item["id"], "quantity": item["quantity"]}],
        "status": "PENDING"
    }

    return {
        "merchantOrderId": order_id,
        "channel": "ACME_WEB",
        "deviceSessionId": session_id,
        "creationDateTime": now,
        "userIp": ip_address,
        "account": {
            "id": uuid.uuid4().hex,
            "type": "STANDARD",
            "creationDateTime": now,
            "username": fake.user_name(),
            "accountIsActive": True
        },
        "items": [item],
        "fulfillment": [fulfillment],
        "transactions": [transaction],
        "promotions": [],
        "loyalty": {
            "id": uuid.uuid4().hex,
            "description": "Pizza Points",
            "credit": {
                "creditType": "GIFT_CARD",
                "amount": "100",
                "currency": "USD"
            }
        },
        "customFields": {
            "keyNumber": fake.random_int(1, 100),
            "keyBoolean": True,
            "keyString": fake.word(),
            "keyDate": now
        }
    }

def generate_update_order_record(order):
    update_order = {
        "merchantOrderId": order["merchantOrderId"],
        "deviceSessionId": order["deviceSessionId"],
        "riskInquiry": {
            "decision": random.choice(["APPROVED", "DECLINED"])
        },
        "transactions": [
            {
                "transactionId": order["transactions"][0]["merchantTransactionId"],
                "payment": order["transactions"][0]["payment"],
                "authorizationStatus": {
                    "authResult": random.choice(["APPROVED", "DECLINED", "ERROR", "UNKNOWN"]),
                    "verificationResponse": {
                        "cvvStatus": random.choice(["MATCH", "NO_MATCH", "NOT_PROVIDED", "NOT_CHECKED", "UNKNOWN"]),
                        "avsStatus": random.choice(["A", "N", "Y", "Z", "X", "W", "U", "S", "R"])
                    },
                    "processorResponse": {
                        "code": fake.lexify(text="??"),
                        "message": fake.sentence()
                    }
                }
            }
        ],
        "fulfillment": [
            {
                "fulfillmentId": order["merchantOrderId"],
                "status": random.choice(["PENDING", "FULFILLED", "CANCELED", "PARTIALLY_FULFILLED"]),
                "accessUrl": fake.url(),
                "shipping": order["fulfillment"][0]["shipping"],
                "digitalDownloaded": random.choice([True, False]),
                "downloadDeviceIp": order["userIp"]
            }
        ],
        "updateDateTime": datetime.utcnow().isoformat() + "Z",
        "updateReason": "Customer requested change"
    }
    return update_order

# Generate 50 synthetic records with alternating order and update entries
combined_records = []
for _ in range(50):
    order = generate_record()
    update = generate_update_order_record(order)
    combined_records.append({"type": "OrderRequest", "payload": order})
    combined_records.append({"type": "UpdateOrderRequest", "payload": update})

# Save to a single file
with open("combined_order_requests.json", "w", encoding='utf-8') as f:
    json.dump(combined_records, f, indent=2)

print("Generated 50 Orders API requests each followed by a corresponding Update Order request.")