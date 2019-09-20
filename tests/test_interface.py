import json
import tempfile
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
        self.assertIs(inter.get('/nonexistent'), None)

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
        sub.set('/c', 'C')
        self.assertEqual(sub.get('/c'), 'C')
        sub.delete('/a')
        self.assertEqual(sub.get('/'), {'b': 'B', 'c': 'C'})


class TestJsonInterface(unittest.TestCase):
    def setUp(self) -> None:
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
        self.file = tempfile.NamedTemporaryFile(mode='w+', encoding='utf8')
        json.dump(self.data, self.file)
        self.file.flush()

    def test_init(self):
        inter = interface.JsonInterface(self.file.name)
        self.assertEqual(inter.get('/'), self.data)

    def test_write(self):
        inter = interface.JsonInterface(self.file.name)
        inter.set('/newkey', 'something')
        inter.write()
        new = interface.JsonInterface(self.file.name)
        self.assertEqual(new.get('/newkey'), 'something')

    def tearDown(self) -> None:
        self.file.close()


class TestLinkedInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.data1 = {
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
        self.data2 = {
            "string": "other",
            "list": [
                "some",
                "more"
            ],
            "dict": {
                'x': 'X',
                'y': 'Y'
            }
        }
        self.file1 = tempfile.NamedTemporaryFile(mode='w+', encoding='utf8')
        json.dump(self.data1, self.file1)
        self.file1.flush()
        self.file2 = tempfile.NamedTemporaryFile(mode='w+', encoding='utf8')
        json.dump(self.data2, self.file2)
        self.file2.flush()

    def test_create(self):
        inter1 = interface.JsonInterface(self.file1.name)
        inter2 = interface.JsonInterface(self.file2.name)
        linked = interface.LinkedInterface(inter1, inter2)
        alt = inter1 + inter2
        self.assertEqual(linked.searchpath, alt.searchpath)

    def test_get(self):
        inter1 = interface.JsonInterface(self.file1.name)
        inter2 = interface.JsonInterface(self.file2.name)
        linked = interface.LinkedInterface(inter1, inter2)
        self.assertEqual(linked.get('/string'), 'other')
        self.assertEqual(linked.get('/list/0'), 'some')

    def test_get_all(self):
        inter1 = interface.JsonInterface(self.file1.name)
        inter2 = interface.JsonInterface(self.file2.name)
        linked = interface.LinkedInterface(inter1, inter2)
        self.assertEqual(linked.get('*:/string'), ['value', 'other'])
        self.assertEqual(linked.get('*:/list'), ['string', 1, None, True, 'some', 'more'])
        self.assertEqual(linked.get('*:/dict'), {'a': 'A', 'b': 'B', 'x': 'X', 'y': 'Y'})

    def test_get_specific(self):
        inter1 = interface.JsonInterface(self.file1.name)
        inter2 = interface.JsonInterface(self.file2.name)
        linked = interface.LinkedInterface(inter1, inter2)
        self.assertEqual(linked.get(str(inter1.filename) + ':/string'), 'value')

    def tearDown(self) -> None:
        self.file1.close()
        self.file2.close()


if __name__ == '__main__':
    unittest.main()
