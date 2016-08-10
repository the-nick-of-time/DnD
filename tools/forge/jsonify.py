import json

class Encoder(json.JSONEncoder):
    def default(self, obj):
        d = {'__class__': obj.__class__.__name__,
             '__module__': obj.__module__
             }
        d.update(obj.__dict__)
        return d


class Decoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.make_objects)
        
    def make_objects(self, d):
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            inst = class_(**d)
        else:
            inst = d
        return inst
        
    def 