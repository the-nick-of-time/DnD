import unittest

from DnD.modules.lib import interface


class TestDataInterface(unittest.TestCase):
    def setUp(self) -> None:
        # Sample data to be used in each method
        self.data = {
            "string": "value",
            "dict": {
                "a": "A",
                "b": "B"
            },
            "list": [
                "string",
                1,
                None,
                True
            ]
        }

    def test_get(self):
        inter = interface.DataInterface(self.data)
        self.assertEqual(inter.get('/string'), 'value')
        self.assertEqual(inter.get('/dict/a'), 'A')
        self.assertEqual(inter.get('/list/3'), True)
        self.assertEqual(inter.get('/'), self.data)

    def test_set(self):
        inter = interface.DataInterface(self.data)
        inter.set('/dict/a', 'New A')
        self.assertEqual(self.data['dict']['a'], 'New A')
        inter.set('/dict', 'a dict no longer')
        self.assertEqual(self.data['dict'], 'a dict no longer')
        inter.set('/new', "new value")
        self.assertEqual(self.data['new'], 'new value')
        inter.set('/', "nothing remains")
        self.assertEqual(inter.get('/'), "nothing remains")

    def test_delete(self):
        inter = interface.DataInterface(self.data)
        inter.delete('/dict/a')
        self.assertEqual(self.data['dict'], {'b': 'B'})
        inter.delete('/list/1')
        self.assertEqual(self.data['list'], ['string', None, True])
        inter.delete('/')
        self.assertEqual(inter.get('/'), {})

    def test_cd(self):
        inter = interface.DataInterface(self.data)
        sub = inter.cd('/dict')
        self.assertEqual(sub.get('/a'), 'A')
        self.assertEqual(sub.get('/'), {'a': 'A', 'b': 'B'})


if __name__ == '__main__':
    unittest.main()
