from faker import Faker
import random
import pandas as pd
from datetime import datetime
import uuid

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

# Generate 50 synthetic records
records = [generate_record() for _ in range(50)]

# Convert to DataFrame for easy manipulation/export
df = pd.DataFrame(records)
df.to_csv('synthetic.csv', index=False)

print(df.head())