import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from models.user import User
from controllers.api import API
import uuid

class TestAPIMethods(unittest.TestCase):
    def test_crear_api(self):
        api = API()
        self.assertIsNotNone(api)

    def test_registra_usuario(self):
        user = User(
            name=str(uuid.uuid4()),
            password=str(uuid.uuid4()),
            username=str(uuid.uuid4())
        )
        api = API()
        self.assertTrue(api.registrar_usuario(user.get_body()))

    def test_login_falla(self):
        api = API()
        self.assertIsNotNone(api)
        user = User(
            name=str(uuid.uuid4()),
            password=str(uuid.uuid4()),
            username=str(uuid.uuid4())
        )
        self.assertTrue(api.registrar_usuario(user.get_body()))
        self.assertTrue(api.login(user=user.username, password='foo') == None)
        
    def test_login_ok(self):
        api = API()
        self.assertIsNotNone(api)
        user = User(
            name=str(uuid.uuid4()),
            password=str(uuid.uuid4()),
            username=str(uuid.uuid4())
        )
        self.assertTrue(api.registrar_usuario(user.get_body()))
        
        self.assertEqual(api.login(user=user.username, password=user.password), user.get_body())
        
if __name__ == '__main__':
    unittest.main()