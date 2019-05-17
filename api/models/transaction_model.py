import mongoengine as db
import mongoengine_goodjson as gj
from datetime import datetime


class Item(db.EmbeddedDocument):
    name = db.StringField(required=True)
    price = db.DecimalField(required=True)
    quantity = db.DecimalField()


class Transaction(gj.Document):
    user = db.ReferenceField('User')
    items = db.ListField(db.EmbeddedDocumentField(Item))
    created_at = db.DateTimeField(default=datetime.utcnow)
    last_modified_at = db.DateTimeField(default=datetime.utcnow)
    meta = {'collection': 'transactions'}

    def save(self, *args, **kwargs):
        self.last_modified_at = datetime.utcnow()
        return super(Transaction, self).save(*args, **kwargs)
