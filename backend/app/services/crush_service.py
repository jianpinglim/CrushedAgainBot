from datetime import datetime
from typing import Optional
from .models import Crush
import logging

logger = logging.getLogger(__name__)


class CrushService:
    def __init__(self, database_utility):
        self._database_utility = database_utility

    def insert_crush(
        self,
        user_telegram_id: int,
        crush_user_id: int,
    ):


        new_entry = Crush(
            user_telegram_id=user_telegram_id,
            crush_user_id=crush_user_id,
        )

        with self._database_utility.session_scope() as session:
            # Check if the user already exists
            if session.query(Crush).filter(Crush.user_telegram_id == user_telegram_id).first():
                return "Already exists"

            session.add(new_entry)

            # This will populate the id of the new entry
            session.flush()

            logger.info(
                f"Added new user entry with ID {new_entry.crush_id}, crush_user_id={new_entry.crush_user_id}, user_telegram_id={new_entry.user_telegram_id})"
            )

            return new_entry.crush_id

        return None

    def get_all_telegram_id(self):
        """
        Retrieve all prediction telegram user entries from the database.
        """
        with self._database_utility.session_scope() as session:
            # entries = Entry.query.all() # version 2
            entries = (
                session.execute(
                    self._database_utility.db.select(Crush).order_by(
                        Crush.crush_id
                    )
                )
                .scalars()
                .all()
            )

            # Convert to list of dictionaries within the session scope
            entries_dict = [entry.to_dict() for entry in entries]

            logger.info(f"Retrieved {len(entries)} user entries")

            return entries_dict

    def get_by_user_telegram_id(self, telegram_id: int):
        """
        Retrieve a single user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            # Retrieve the user with the given ID
            entry = session.query(Crush).filter_by(user_telegram_id=telegram_id).first()

            if entry:
                logger.info(f"Retrieved user entry with ID {telegram_id}")
                return entry.to_dict()
            else:
                logger.warning(f"No user entry found with ID {telegram_id}")
                return None

    def get_by_crush_user_id(self, crush_user_id: int):
        """
        Retrieve a single user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(crush_user_id, int) or crush_user_id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            # Retrieve the user with the given ID
            entries = session.query(Crush).filter_by(crush_user_id=crush_user_id).all()
            # Convert to list of dictionaries within the session scope
            entries_dict = [entry.to_dict() for entry in entries]

            if entries:
                logger.info(f"Retrieved user entry with ID {crush_user_id}")
                return entries_dict
            else:
                logger.warning(f"No user entry found with ID {crush_user_id}")
                return None

    def delete_by_telegram_id(self, telegram_id: int) -> bool:
        """
        Delete a user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            entry = session.query(Crush).filter_by(user_telegram_id=telegram_id).first()
            if entry:
                session.delete(entry)
                logger.info(f"Deleted user entry with ID {telegram_id}")
                return True
            else:
                logger.warning(f"No user entry found with ID {telegram_id}")
                return False

    def delete_all_crushes(self) -> int:
        """
        Delete all crushes entries.
        """
        with self._database_utility.session_scope() as session:
            num_deleted = session.query(Crush).delete()
            logger.info(f"Deleted {num_deleted} crushes entries")
            return num_deleted

    def update_crush(self, user_telegram_id: int, new_crush_user_id: str) -> bool:
        """
        Update a user entry by its telegram_id.
        """
        with self._database_utility.session_scope() as session:
            entry = session.query(Crush).where(
                Crush.user_telegram_id == user_telegram_id
            ).all()

            if len(entry) != 0:
                old_crush_user_id = entry[0].crush_user_id
                entry[0].crush_user_id = new_crush_user_id
                logger.info(f"Updated user {user_telegram_id} entry from {old_crush_user_id} to {entry[0].crush_user_id}")
                return True
            else:
                logger.warning(
                    f"user entry with user_telegram_id {user_telegram_id} not found")
                return False
