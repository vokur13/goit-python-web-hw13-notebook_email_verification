from typing import List, Annotated


from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Query,
    Path,
)

from sqlalchemy.orm import Session


from src.db.models import User
from src.repository import contacts as depo_contacts
from src.db.database import get_db
from src.schemas.contacts import Contact, ContactCreate
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    db_contact = await depo_contacts.get_contact_by_email(
        db, user=current_user, email=contact.email
    )
    if db_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return await depo_contacts.create_contact(user=current_user, db=db, contact=contact)


@router.get("", response_model=List[Contact])
async def read_contacts(
    skip: int = 0,
    limit: int = Query(10, le=100),
    email: Annotated[str | None, Query(max_length=255)] = None,
    first_name: Annotated[str | None, Query(max_length=255)] = None,
    last_name: Annotated[str | None, Query(max_length=255)] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await depo_contacts.get_contacts(
        db,
        email,
        current_user,
        first_name,
        last_name,
        skip,
        limit,
    )


@router.get("/week_to_birthday", response_model=List[Contact])
async def read_contacts_by_week_to_birthday(
    skip: int = 0,
    limit: int = Query(10, le=100),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    return await depo_contacts.read_contacts_by_week_to_birthday(
        db=db, skip=skip, limit=limit, user=current_user
    )


@router.get("/{contact_id}", response_model=Contact)
async def read_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    db_contact = await depo_contacts.get_contact(
        db, user=current_user, contact_id=contact_id
    )
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return db_contact


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact: ContactCreate,
    contact_id: int = Path(ge=1),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    db_contact = await depo_contacts.get_contact(
        db, user=current_user, contact_id=contact_id
    )
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return await depo_contacts.update_contact(db_contact, contact, db)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    db_contact = await depo_contacts.get_contact(
        db, contact_id=contact_id, user=current_user
    )
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return await depo_contacts.remove_contact(db_contact, db)
