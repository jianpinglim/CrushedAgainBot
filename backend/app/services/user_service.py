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
        username: str,
        hashed_password: str,
        email: str,
        phone_number: str,
        points: int,
    ):

        # The above checks are performed before creating a new user entry in the database to maintain data integrity.
        from .models import UserInfo

        new_entry = UserInfo(
            username=username,
            hashed_password=hashed_password,
            email=email,
            phone_number=phone_number,
            points=points,
        )

        with self._database_utility.session_scope() as session:
            # Check if the username already exists
            if session.query(UserInfo).filter(UserInfo.username == username).first():
                return "Already exists"

            session.add(new_entry)

            # This will populate the id of the new entry
            session.flush()

            logger.info(
                f"Added new user entry with ID {new_entry.user_id}, username={new_entry.username}, hashed_password={new_entry.hashed_password}, email={new_entry.email}, created_on={new_entry.created_on}, phone_number={new_entry.phone_number}, points={new_entry.points})"
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

    def get_by_user_id(self, id: int):
        """
        Retrieve a single user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(id, int) or id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            # Retrieve the user with the given ID
            entry = session.get(UserInfo, id)

            if entry:
                logger.info(f"Retrieved user entry with ID {id}")
                return entry.to_dict()
            else:
                logger.warning(f"No user entry found with ID {id}")
                return None

    def delete_by_user_id(self, id: int) -> bool:
        """
        Delete a user entry by its ID.
        """
        # Ensures that the provided id is a valid positive integer
        if not isinstance(id, int) or id <= 0:
            logger.error("Invalid input: ID must be a positive integer")
            raise ValueError("ID must be a positive integer")

        with self._database_utility.session_scope() as session:
            entry = session.get(UserInfo, id)
            if entry:
                session.delete(entry)
                logger.info(f"Deleted user entry with ID {id}")
                return True
            else:
                logger.warning(f"No user entry found with ID {id}")
                return False

    def delete_all_user(self) -> int:
        """
        Delete all user entries.
        """
        with self._database_utility.session_scope() as session:
            num_deleted = session.query(UserInfo).delete()
            logger.info(f"Deleted {num_deleted} User entries")
            return num_deleted

    def update_user_points(self, user_id: int) -> bool:
        """
        Update a user entry by its user_id.
        """
        with self._database_utility.session_scope() as session:
            entry = session.query(UserInfo).where(
                UserInfo.user_id == user_id
            ).all()

            if len(entry) != 0:
                entry[0].points += 1
                logger.info(f"Updated user {user_id} entry to {entry[0].points} points")
                return True
            else:
                logger.warning(
                    f"user entry with user_id {user_id} not found")
                return False
