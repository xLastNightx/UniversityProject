from sqlalchemy.orm import Session
from . import models, schemas


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email, 
        name=user.name,
        google_sub=user.google_sub if user.google_sub else ""
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_booking(db: Session, booking: schemas.BookingCreate, user_email: str):
    db_booking = models.Booking(
        user_email=user_email,
        date=booking.date,
        time_slot=booking.time_slot,
        confirmed=True
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_bookings_by_user(db: Session, email: str, skip: int = 0, limit: int = 10):
    return db.query(models.Booking).filter(
        models.Booking.user_email == email
    ).offset(skip).limit(limit).all()


def get_booking_by_id(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()


def delete_booking(db: Session, booking_id: int):
    booking = get_booking_by_id(db, booking_id)
    if booking:
        db.delete(booking)
        db.commit()
        return True
    return False


def get_all_bookings_on_date(db: Session, date: str):
    return db.query(models.Booking).filter(models.Booking.date == date).all()
