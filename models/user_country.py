from sqlalchemy import Column, Integer, String

from .base import Base, engine


class UserCountry(Base):
    __tablename__ = "user_country"

    user_id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False)
    country_iso_2 = Column(String, nullable=False)

    @classmethod
    def get_user_country(cls, user_id, session):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    def add(cls, user_id: int, country: str, country_iso_2: str, session: object):
        """Add a new user-country pair to the database."""

        session.add(cls(user_id=user_id, country=country, country_iso_2=country_iso_2))
        session.commit()

    @classmethod
    def get_country(cls, user_id: int, session: object) -> str:
        """Get a country from the database."""

        user = session.query(cls).filter_by(user_id=user_id).first()
        if not user:
            return None
        return user.country_iso_2


if __name__ == "__main__":
    Base.metadata.create_all(engine)  # Create the table in the database.
