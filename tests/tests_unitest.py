import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.emtity.models import Base, Users, Contact
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    search_contact,
    upcoming_birthdays,
)
from src.schemas.contact import ContactCreate


class TestApiFunctions(unittest.TestCase):

    def setUp(self):
        # Используем тестовую базу данных в памяти
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.db = session()

    def tearDown(self):
        # Очищаем базу данных после каждого теста
        self.db.close_all()
        Base.metadata.drop_all(self.engine)

    def test_get_contacts(self):
        # Создаем фиктивного пользователя для теста
        user = Users(id=1, username='test_user')
        self.db.add(user)

        # Создаем несколько контактов для пользователя
        contacts = [Contact(user=user) for _ in range(5)]
        self.db.add_all(contacts)
        self.db.commit()

        # Проверяем функцию получения контактов
        retrieved_contacts = get_contacts(limit=10, offset=0, db=self.db, user=user)
        self.assertEqual(len(retrieved_contacts), 5)

    def test_get_contact(self):
        # Создаем фиктивного пользователя и контакт для теста
        user = Users(id=1, username='test_user')
        contact = Contact(id=1, user=user)
        self.db.add_all([user, contact])
        self.db.commit()

        # Проверяем функцию получения одного контакта
        retrieved_contact = get_contact(contact_id=1, db=self.db, user=user)
        self.assertEqual(retrieved_contact.id, 1)

    # Добавьте аналогичные тесты для остальных функций API

    def test_create_contact(self):
        # Создаем фиктивного пользователя для теста
        user = Users(id=1, username='test_user')
        self.db.add(user)
        self.db.commit()

        # Создаем данные для нового контакта
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
        contact_create = ContactCreate(**contact_data)

        # Проверяем функцию создания контакта
        created_contact = create_contact(body=contact_create, db=self.db, user=user)
        self.assertEqual(created_contact.first_name, "John")
        self.assertEqual(created_contact.last_name, "Doe")

    # Также добавьте тесты для update_contact, delete_contact, search_contact и upcoming_birthdays
    def test_update_contact(self):
        # Создаем фиктивного пользователя и контакт для теста
        user = Users(id=1, username='test_user')
        contact = Contact(id=1, user=user)
        self.db.add_all([user, contact])
        self.db.commit()

        # Подготавливаем данные для обновления контакта
        updated_data = {
            "first_name": "UpdatedJohn",
            "last_name": "UpdatedDoe",
            "email": "updatedjohn@example.com"
        }
        updated_contact = ContactCreate(**updated_data)

        # Проверяем функцию обновления контакта
        updated_contact = update_contact(contact_id=1, body=updated_contact, db=self.db, user=user)
        self.assertEqual(updated_contact.first_name, "UpdatedJohn")
        self.assertEqual(updated_contact.last_name, "UpdatedDoe")

    def test_delete_contact(self):
        # Создаем фиктивного пользователя и контакт для теста
        user = Users(id=1, username='test_user')
        contact = Contact(id=1, user=user)
        self.db.add_all([user, contact])
        self.db.commit()

        # Проверяем функцию удаления контакта
        delete_result = delete_contact(contact_id=1, db=self.db, user=user)

        # Проверяем, что контакт был успешно удален
        self.assertEqual(delete_result, {"message": "Контакт видалено успішно"})

        # Пытаемся получить удаленный контакт (должно вернуться None)
        retrieved_contact = self.db.query(Contact).filter_by(id=1).first()
        self.assertIsNone(retrieved_contact)

    def test_search_contact(self):
        # Создаем фиктивного пользователя и несколько контактов для теста
        user = Users(id=1, username='test_user')
        contacts = [
            Contact(first_name="John", last_name="Doe", email="john@example.com", user=user),
            Contact(first_name="Jane", last_name="Doe", email="jane@example.com", user=user),
            Contact(first_name="Alice", last_name="Smith", email="alice@example.com", user=user),
        ]
        self.db.add_all([user] + contacts)
        self.db.commit()

        # Проверяем функцию поиска контактов по запросу
        search_result = search_contact(query="Doe", db=self.db, user=user)

        # Проверяем, что функция вернула правильное количество контактов по запросу
        self.assertEqual(len(search_result), 2)

        # Проверяем, что поиск работает корректно для введенного запроса
        self.assertTrue(all(
            contact.email == "john@example.com" or contact.email == "jane@example.com" for contact in search_result))

    def test_upcoming_birthdays(self):
        # Создаем фиктивного пользователя и несколько контактов с днями рождения для теста
        user = Users(id=1, username='test_user')
        today = datetime.now().date()
        contacts = [
            Contact(first_name="John", last_name="Doe", email="john@example.com", user=user,
                    birthday=today + timedelta(days=3)),
            Contact(first_name="Jane", last_name="Doe", email="jane@example.com", user=user,
                    birthday=today + timedelta(days=5)),
            Contact(first_name="Alice", last_name="Smith", email="alice@example.com", user=user,
                    birthday=today + timedelta(days=10)),
        ]
        self.db.add_all([user] + contacts)
        self.db.commit()

        # Проверяем функцию upcoming_birthdays
        upcoming_bdays = upcoming_birthdays(db=self.db, user=user)

        # Проверяем, что функция вернула правильное количество контактов с предстоящими днями рождения
        self.assertEqual(len(upcoming_bdays), 2)

        # Проверяем, что контакты возвращаются в правильной последовательности по датам дней рождения
        self.assertTrue(upcoming_bdays[0].birthday < upcoming_bdays[1].birthday)


if __name__ == '__main__':
    unittest.main()
