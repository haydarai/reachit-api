import os
from api.models.user_model import User
from api.models.transaction_model import Transaction
from api.models.promotion_model import Promotion
from mongoengine import connect
from SPARQLWrapper import SPARQLWrapper, JSON
from faker import Faker
import random
from dotenv import load_dotenv
import app
load_dotenv()

connect(host=os.getenv('MONGODB_URI'))

sparql = SPARQLWrapper(os.getenv('SPARQL_ENDPOINT'))
sparql.addDefaultGraph(os.getenv('SPARQL_GRAPH'))
sparql.setReturnFormat(JSON)

sparql.setQuery("""
    PREFIX ri: <http://www.reach-it.com/ontology/>

    SELECT ?m ?mn
    WHERE {
        ?m ri:merchantName ?mn
        FILTER (lang(?mn) = 'en')
    }
""")
merchants_results = sparql.query().convert()

sparql.setQuery("""
    PREFIX ri: <http://www.reach-it.com/ontology/>

    SELECT ?pn
    WHERE {
        ?p ri:productName ?pn
        FILTER (lang(?pn) = 'en')
    }
""")
products_results = sparql.query().convert()

sparql.setQuery("""
    PREFIX ri: <http://www.reach-it.com/ontology/>

    SELECT ?pcn
    WHERE {
        ?pc ri:categoryName ?pcn
        FILTER (lang(?pcn) = 'en')
    }
""")
categories_results = sparql.query().convert()

sparql.setQuery("""
    PREFIX ri:<http://www.reach-it.com/ontology/>

    SELECT ?address ?merchantName ?cityName ?countryName
    WHERE {
        ?merchant ri:merchantName ?merchantName .
        ?store ri:locatedInCity ?city .
        ?city ri:cityName ?cityName .
        ?store ri:storeAddress ?address .
        ?city ri:isInCountry ?country .
        ?country ri:countryName ?countryName 
        FILTER(lang(?address) = 'en' && lang(?merchantName) = 'en' && lang(?cityName) = 'en' && lang(?countryName) = 'en')
    }
""")
stores_results = sparql.query().convert()

fake = Faker()

random_stores = stores_results['results']['bindings'][0:3]
random_products = products_results['results']['bindings'][0:100]
random_categories = categories_results['results']['bindings'][0:3]

for _ in range(10):
    email = fake.email()
    name = fake.name()
    user = User.objects(pk=email).first()
    password = app.bcrypt.generate_password_hash('password').decode('utf-8')

    if not user:
        user = User(email=email, name=name,
                    user_type='user', password=password)
        user.save()

        t = random.randint(1, 5)
        for __ in range(t):
            picked_store = random.choice(random_stores)
            picked_products = random.choices(random_products, k=t)
            items = []

            for i in range(t):
                name = picked_products[i]['pn']['value']
                item = {
                    'name': name,
                    'currency': 'EUR',
                    'price': random.randint(1, 10),
                    'quantity': random.randint(1, 3)
                }
                items.append(item)

            location = picked_store['address']['value']
            merchant = picked_store['merchantName']['value']
            city = picked_store['cityName']['value']
            country = picked_store['countryName']['value']

            transaction = Transaction(
                user=email, items=items, location=location, merchant=merchant, city=city, country=country)
            transaction.save()


for result in merchants_results['results']['bindings']:
    merchant_email = 'admin@' + \
        result['m']['value'].rsplit(
            '/')[-1].lower().replace('_', '').replace(' ', '') + '.com'
    merchant_name = result['mn']['value']
    user = User.objects(pk=merchant_email).first()
    password = app.bcrypt.generate_password_hash('password').decode('utf-8')

    if not user:
        user = User(email=merchant_email, name=merchant_name,
                    user_type='merchant', password=password)
        user.save()

    k = random.randint(1, 2)
    for __ in range(k):
        picked_category = random.choice(random_categories)['pcn']['value']
        title = fake.sentence()
        description = fake.paragraph()
        image = 'https://picsum.photos/500/500'
        promotion = Promotion(creator=merchant_email,
                            title=title, description=description, image=image)
        promotion.save()