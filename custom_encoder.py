import json
from decimal import Decimal

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) #return a float version of that decimal
        
        return json.JSONEncoder.default(self, obj)
