from datetime import datetime
from typing import Optional
from .models import UserInfo
import logging

logger = logging.getLogger(__name__)


class UserInfoService:
    def __init__(self, database_utility):
        self._database_utility = database_utility

    def insert_user(
        self,
        user_telegram_id: int,
        username: str,
    ):

        # The above checks are performed before creating a new user entry in the database to maintain data integrity.
        from .models import UserInfo

        new_entry = UserInfo(
            user_telegram_id=user_telegram_id,
            username=username,
        )

        with self._database_utility.session_scope() as session:
            # Check if the user already exists
            if session.query(UserInfo).filter(UserInfo.user_telegram_id == user_telegram_id).first():
                return "Already exists"

            session.add(new_entry)

            # This will populate the id of the new entry
            session.flush()

            logger.info(
                f"Added new user entry with ID {new_entry.user_id}, username={new_entry.username}, user_telegram_id={new_entry.user_telegram_id})"
            )

            return new_entry.user_id

        return None

    def get_all_user(self):
        """
        Retrieve all prediction user entries from the database.
        """
        with self._database_utility.session_scope() as session:
            # entries = Entry.query.all() # version 2
            entries = (
                session.execute(
                    self._database_utility.db.select(UserInfo).order_by(
                        UserInfo.user_id
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
            entry = session.query(UserInfo).filter_by(user_telegram_id=telegram_id).first()

            if entry:
                logger.info(f"Retrieved user entry with ID {telegram_id}")
                return entry.to_dict()
            else:
                logger.warning(f"No user entry found with ID {telegram_id}")
                return None

    def delete_by_user_telegram_id(self, telegram_id: int) -> bool:
        """
        Delete a user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            entry = session.query(UserInfo).filter_by(user_telegram_id=telegram_id).first()
            if entry:
                session.delete(entry)
                logger.info(f"Deleted user entry with ID {telegram_id}")
                return True
            else:
                logger.warning(f"No user entry found with ID {telegram_id}")
                return False

    def delete_all_user(self) -> int:
        """
        Delete all user entries.
        """
        with self._database_utility.session_scope() as session:
            num_deleted = session.query(UserInfo).delete()
            logger.info(f"Deleted {num_deleted} User entries")
            return num_deleted

    def update_username(self, telegram_id: int, new_username: str) -> bool:
        """
        Update a user entry by its telegram_id.
        """
        with self._database_utility.session_scope() as session:
            entry = session.query(UserInfo).where(
                UserInfo.user_telegram_id == telegram_id
            ).all()

            if len(entry) != 0:
                old_username = entry[0].username
                entry[0].username = new_username
                logger.info(f"Updated user {telegram_id} entry from {old_username} to {entry[0].username}")
                return True
            else:
                logger.warning(
                    f"user entry with telegram_id {telegram_id} not found")
                return False
