import unittest
from unittest.mock import MagicMock

from faker import Faker
from sqlalchemy.orm import Session

from src.db.models import User
from src.repository.users import get_user_by_email, create_user, update_token
from src.schemas.users import UserCreate

fake = Faker('en_UK')


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=fake.random_digit(), email=fake.email(), password=fake.pystr(), avatar=fake.url(),
                         refresh_token=fake.pystr(max_chars=100),
                         confirmed=True)

    async def test_get_user_by_email_found(self):
        user_by_email = User()
        self.session.query().filter().first.return_value = user_by_email
        result = await get_user_by_email(db=self.session, email=user_by_email.email)
        self.assertEqual(result, user_by_email)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email=fake.email(), db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserCreate(
            email=fake.email(),
            password=fake.pystr()
        )
        result = await create_user(body=body, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_update_token(self):
        user = User(
            email=fake.email(),
            password=fake.pystr()
        )
        result = await update_token(user=user, token=fake.pystr(max_chars=100), db=self.session)

        self.assertNotEqual(result, user)


if __name__ == '__main__':
    unittest.main()
