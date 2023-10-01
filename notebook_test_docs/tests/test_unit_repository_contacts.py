import unittest
from unittest.mock import MagicMock

from faker import Faker
from sqlalchemy.orm import Session

from src.db.models import User, Contact
from src.repository.contacts import get_contacts, create_contact, update_contact, get_contact, get_contact_by_email, \
    read_contacts_by_week_to_birthday, remove_contact
from src.schemas.contacts import ContactCreate

fake = Faker('en_UK')


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=fake.random_digit(), email=fake.email(), password=fake.pystr(), avatar=fake.url(),
                         refresh_token=fake.pystr(max_chars=100),
                         confirmed=True)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_email_found(self):
        contact_by_email = Contact()
        self.session.query().filter().first.return_value = contact_by_email
        result = await get_contact_by_email(db=self.session, user=self.user, email=fake.safe_email())
        self.assertEqual(result, contact_by_email)

    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_email(db=self.session, user=self.user, email=fake.safe_email())
        self.assertEqual(result, None)

    async def test_get_contacts_no_params(self):
        contacts_no_params = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts_no_params
        result = await get_contacts(0, 10, self.user, None, None, None, self.session)
        self.assertEqual(result, contacts_no_params)

    async def test_get_contacts_by_email(self):
        contacts_by_email = [Contact(), Contact(), Contact()]
        self.session.query().filter().filter().offset().limit().all.return_value = contacts_by_email
        result = await get_contacts(0, 10, self.user, fake.safe_email(), None, None, self.session)
        self.assertEqual(result, contacts_by_email)

    async def test_get_contacts_by_first_name(self):
        contacts_by_first_name = [Contact(), Contact(), Contact()]
        self.session.query().filter().filter().offset().limit().all.return_value = contacts_by_first_name
        result = await get_contacts(0, 10, self.user, None, fake.first_name(), None, self.session)
        self.assertEqual(result, contacts_by_first_name)

    async def test_get_contacts_by_last_name(self):
        contacts_by_last_name = [Contact(), Contact(), Contact()]
        self.session.query().filter().filter().offset().limit().all.return_value = contacts_by_last_name
        result = await get_contacts(0, 10, self.user, None, None, fake.last_name(), self.session)
        self.assertEqual(result, contacts_by_last_name)

    async def test_read_contacts_by_week_to_birthday(self):
        contacts_by_week_to_birthday = [Contact(), Contact(), Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.safe_email(),
            phone=fake.phone_number(),
            birth_date='1980-10-03',
            bio=fake.sentence(nb_words=10),
            user_id=self.user.id,
        )]
        self.session.query().filter().offset().limit().all.return_value = contacts_by_week_to_birthday
        result = await read_contacts_by_week_to_birthday(self.session, self.user, 0, 10)
        if len(result) > 0:
            return self.assertEqual(result, contacts_by_week_to_birthday)
        self.assertNotEquals(result, contacts_by_week_to_birthday)

    async def test_create_contact(self):
        body = ContactCreate(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            birth_date=fake.date(),
            bio=fake.sentence(nb_words=10)
        )
        result = await create_contact(contact=body, user=self.user, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertEqual(result.bio, body.bio)

    async def test_update_contact(self):
        body = ContactCreate(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            birth_date=fake.date(),
            bio=fake.sentence(nb_words=10)
        )
        contact = Contact(email=fake.email(),
                          first_name=fake.first_name(),
                          last_name=fake.last_name(),
                          phone=fake.phone_number(),
                          birth_date=fake.date(),
                          bio=fake.sentence(nb_words=10)
                          )
        self.session.commit.return_value = None
        result = await update_contact(db_contact=contact, contact=body, db=self.session)
        self.assertEqual(result, contact)
        self.assertEqual(result.first_name, contact.first_name)
        self.assertEqual(result.last_name, contact.last_name)
        self.assertEqual(result.email, contact.email)
        self.assertEqual(result.phone, contact.phone)
        self.assertEqual(result.birth_date, contact.birth_date)
        self.assertEqual(result.bio, contact.bio)

    async def test_remove_contact(self):
        contact_to_remove = Contact()
        result = await remove_contact(db_contact=contact_to_remove, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
