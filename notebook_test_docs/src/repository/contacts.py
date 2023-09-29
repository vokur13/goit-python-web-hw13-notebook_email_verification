from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.db import models
from src.schemas.contacts import ContactCreate


async def get_contact(db: Session, user: models.User, contact_id: int):
    """
    The get_contact function returns a contact from the database.

    :param db: Session: Access the database
    :param user: models.User: Get the user's id to filter the contacts
    :param contact_id: int: Filter the contacts by id
    :return: A contact object
    :doc-author: Trelent"""
    return (
        db.query(models.Contact)
        .filter(
            and_(models.Contact.id == contact_id, models.Contact.user_id == user.id)
        )
        .first()
    )


async def get_contact_by_email(db: Session, user: models.User, email: EmailStr):
    """
    The get_contact_by_email function returns a contact by email.

    :param db: Session: Pass in the database session
    :param user: models.User: Ensure that the user is authenticated
    :param email: EmailStr: Validate the email address
    :return: The first contact in the database that matches the email address and user id
    :doc-author: Trelent"""
    return (
        db.query(models.Contact)
        .filter(and_(models.Contact.email == email, models.Contact.user_id == user.id))
        .first()
    )


async def get_contacts(
        db: Session,
        email: str | None,
        user: models.User,
        first_name: str | None,
        last_name: str | None,
        skip: int,
        limit: int,
):
    """
    The get_contacts function returns a list of contacts that match the search criteria.
        Args:
            db (Session): The database session object.
            email (str | None): The email address to search for in the database. If no value is provided, all contacts are returned.
            user (models.User): The user who owns the contact(s). This is used to ensure that only a single users' contacts are returned and not all users' contacts in the database table/collection/etc..
            first_name (str | None): A string containing part or all of a first name to be searched

    :param db: Session: Pass in the database session
    :param email: str | None: Filter the contacts by email
    :param user: models.User: Get the user id of the current logged-in user
    :param first_name: str | None: Filter the contacts by first name
    :param last_name: str | None: Filter the contacts by last name
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param : Pass in the database session to use for querying
    :return: A list of contacts
    :doc-author: Trelent"""
    contacts = db.query(models.Contact).filter(models.Contact.user_id == user.id)

    if email:
        contacts = contacts.filter(
            and_(
                models.Contact.email.ilike(f"%{email}%"),
                models.Contact.user_id == user.id,
            )
        )
    elif first_name:
        contacts = contacts.filter(
            and_(
                models.Contact.first_name.ilike(f"%{first_name}%"),
                models.Contact.user_id == user.id,
            )
        )
    elif last_name:
        contacts = contacts.filter(
            and_(
                models.Contact.last_name.ilike(f"%{last_name}%"),
                models.Contact.user_id == user.id,
            )
        )
    contacts = contacts.offset(skip).limit(limit).all()
    return contacts


async def read_contacts_by_week_to_birthday(
        db: Session,
        user: models.User,
        skip: int,
        limit: int,
):
    """
    The read_contacts_by_week_to_birthday function returns a list of contacts whose birthdays are within the next week.

    :param db: Session: Pass a database session to the function
    :param user: models.User: Filter the contacts by user_id
    :param skip: int: Skip the first n contacts in the list
    :param limit: int: Limit the number of contacts that are returned
    :param : Get the contacts from a specific user
    :return: A list of contacts whose birthdays are in the next week
    :doc-author: Trelent"""
    current_datetime = datetime.now().date()
    delta = timedelta(days=7)
    future_datetime = current_datetime + delta

    contacts = db.query(models.Contact).filter(
        models.Contact.user_id == user.id,
    )

    bd_list = list()

    for contact in contacts:
        bd = datetime(
            year=current_datetime.year,
            month=contact.birth_date.month,
            day=contact.birth_date.day,
        ).date()
        if (future_datetime - bd) <= delta:
            bd_list.append(contact)

    return bd_list


async def create_contact(user: models.User, contact: ContactCreate, db: Session):
    """
    The create_contact function creates a new contact in the database.

    :param user: models.User: Get the user's id
    :param contact: ContactCreate: Pass in the contact data that is being created
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent"""
    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birth_date=contact.birth_date,
        bio=contact.bio,
        user_id=user.id,
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(
        db_contact, contact: ContactCreate, db: Session
) -> models.Contact | None:
    """
    The update_contact function updates a contact in the database.
        Args:
            db_contact (models.Contact): The contact to be updated in the database.
            contact (ContactCreate): The new information for the existing Contact object, which will overwrite its old data.

    :param db_contact: Pass the contact to be updated
    :param contact: ContactCreate: Pass the contact object to the function
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: Trelent"""
    db_contact.first_name = contact.first_name
    db_contact.last_name = contact.last_name
    db_contact.email = contact.email
    db_contact.phone = contact.phone
    db_contact.birth_date = contact.birth_date
    db_contact.bio = contact.bio
    db.commit()
    return db_contact


async def remove_contact(db_contact, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            db_contact (Contact): The contact to be removed from the database.
            db (Session): A session object for interacting with the database.

    :param db_contact: Pass in the contact we want to delete
    :param db: Session: Pass the database session to the function
    :return: A none, but the delete function returns a number of rows deleted
    :doc-author: Trelent"""
    db.delete(db_contact)
    db.commit()
