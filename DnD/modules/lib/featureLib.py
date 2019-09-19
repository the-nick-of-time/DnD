from . import bonusLib as bon
from . import characterLib as char
from . import interface as iface
from . import resourceLib as res


class OwnedFeatures:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.character = character
        self.features = {name: OwnedFeature(name, filepath, character)
                         for name, filepath in self.record.get('/').items()}

    @property
    def resources(self):
        rv = []
        for feature in self.features.values():
            resource = feature.resource
            if resource is not None:
                rv.append(resource)
        return rv

    @property
    def bonuses(self):
        rv = []
        for feature in self.features.values():
            bonus = feature.bonus
            if bonus is not None:
                rv.append(bonus)
        return rv


class Feature:
    # Will be useful in character creator/level up
    def __init__(self, name: str, filepath: str):
        self.name = name
        file, path = filepath.split(':', 1)
        json = iface.JsonInterface(file, readonly=True)
        self.definition = json.cd(path)
        self.description = self.definition.get('/description')

    @property
    def resource(self):
        if self.definition.get('/resource') is None:
            return None
        # With no writable interface, this will just have access to the definitions
        return res.Resource(None, self.definition.cd('/resource'))

    @property
    def bonus(self):
        if self.definition.get('/bonus') is None:
            return None
        kv = list(self.definition.get('/bonus').items())
        assert len(kv) == 1
        return bon.Bonus(kv[0][0], kv[0][1])


class OwnedFeature(Feature):
    def __init__(self, name: str, filepath: str, character: 'char.Character'):
        super().__init__(name, filepath)
        self.owner = character
        self.record = character.record.cd('/features/' + name, readonly=True)

    @property
    def resource(self):
        return res.OwnedResource(self.record, self.owner, self.definition)
