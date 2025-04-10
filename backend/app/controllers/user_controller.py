from flask.views import MethodView
from flask import jsonify
from flask import request
from flask import session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.services.models import UserInfo
import logging
 
logger = logging.getLogger(__name__)
 
 
class UserController(MethodView):
    def __init__(self, user_service):
        self._user_service = user_service

    def register_user(self):
        logger.info("Handling POST > add")
        data = request.get_json()

        # Extract and validate data from the request JSON
        try:
            username = str(data['username'])
            telegram_id = str(data['telegram_id'])

            if len(telegram_id) != 10:
                raise ValueError("Invalid telegram_id (Must be 10 digits)")

        except KeyError as e:
            logger.error(f"Missing required field: {str(e)}")
            return (
                jsonify(
                    {"success": False, "message": f"Missing required field: {str(e)}"}
                ),
                400,
            )
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            return (
                jsonify({"success": False, "message": f"Invalid input: {str(e)}"}),
                400,
            )

        try:
            # Create a new history entry in the database
            logger.info("Inserting prediction into database")
            db_result = self._user_service.insert_user(
                telegram_id, username 
            )

            # Return JSON object response
            if db_result == "Already exists":
                logger.error("telegram_id already exists")
                return jsonify({"success": False, "message": "telegram_id already exists"}), 400
            elif db_result is not None:
                logger.info(f"Successfully created entry with id: {db_result}")
                return jsonify({"success": True, "id": db_result}), 201
            else:
                logger.error("Failed to create entry")
                return (
                    jsonify({"success": False, "message": "Failed to create entry"}),
                    400,
                )
        except ValueError as e:
            logger.error(f"Error creating entry: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating entry: {str(e)}")
            return jsonify({"error": "Database error occurred"}), 500
        except Exception as e:
            logger.error(f"Unexpected error while adding user: {str(e)}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    
    def get_all_user(self):
        logger.info("Handling GET > get all user")

        try:
            entries = self._user_service.get_all_user()
            logger.info(entries)
            return jsonify(entries), 200
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while retrieving user: {str(e)}"
            )
            return jsonify({"error": "Database error occurred"}), 500
        except Exception as e:
            logger.error(
                f"Unexpected error while retrieving user: {str(e)}"
            )
            return jsonify({"error": "An unexpected error occurred"}), 500
    
    def get_by_telegram_id(self, telegram_id):
        logger.info(f"Handling GET > get user by ID: {telegram_id}")

        try:
            user = self._user_service.get_by_user_telegram_id(telegram_id)
            if user:
                return jsonify({"success": True, "data": user}), 200
            else:
                return (
                    jsonify(
                        {"success": False, "message": f"No user found with ID {telegram_id}"}
                    ),
                    404,
                )
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving user: {str(e)}")
            return (
                jsonify({"success": False, "message": "A database error occurred"}),
                500,
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving user: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "An unexpected error occurred while retrieving the user",
                    }
                ),
                500,
            )
        
    def delete_by_telegram_id(self, telegram_id):
        logger.info("Handling DELETE > delete by some telegram_id")
 
        try:
            result = self._user_service.delete_by_user_telegram_id(telegram_id)
            if result:
                return (
                    jsonify(
                        {
                            "success": True,
                            "message": f"Entry with id {telegram_id} deleted successfully",
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {"success": False, "message": f"No entry found with id {telegram_id}"}
                    ),
                    404,
                )
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting entry: {str(e)}")
            return (
                jsonify({"success": False, "message": "A database error occurred"}),
                500,
            )
        except Exception as e:
            logger.error(f"Error deleting entry: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "An error occurred while deleting the entry",
                    }
                ),
                500,
            )
        
    def delete_all_user(self):
        logger.info("Handling DELETE > delete all")
        try:
            num_deleted = self._user_service.delete_all_user()
 
            return (
                jsonify({"success": True, "message": f"Deleted {num_deleted} entries"}),
                200,
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting all entries: {str(e)}")
            return (
                jsonify({"success": False, "message": "A database error occurred"}),
                500,
            )
        except Exception as e:
            logger.error(f"Unexpected error while deleting all entries: {str(e)}")
            return (
                jsonify({"success": False, "message": "An unexpected error occurred"}),
                500,
            )
        
    def update_user_username(self, telegram_id):
        logger.info("Handling PUT > update username")
        data = request.get_json()

        # Extract and validate data from the request JSON
        try:
            new_username = str(data['new_username'])
            result = self._user_service.update_username(telegram_id, new_username)
            if result:
                return jsonify({"success": True, "message": f"Username updated successfully to {new_username}"}), 200
            else:
                return (
                    jsonify(
                        {"success": False, "message": f"No entry found with id {telegram_id}"}
                    ),
                    404,
                )
        except KeyError as e:
            logger.error(f"Missing required field: {str(e)}")
            return jsonify({"success": False, "message": f"Missing required field: {str(e)}"}), 400
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating user points: {str(e)}")
            return jsonify({"success": False, "message": "A database error occurred"}), 500
        except Exception as e:
            logger.error(f"Unexpected error while updating user points: {str(e)}")
            return jsonify({"success": False, "message": "An unexpected error occurred"}), 500
    
    
    @classmethod
    def register(cls, app, user_service):
        logger.info("register routes")

        # add a user record
        app.add_url_rule(
            "/api/auth/register",
            view_func=cls(user_service).register_user,
            methods=["POST"],
        )

        # get all user records
        app.add_url_rule(
            "/api/auth/",
            view_func=cls(user_service).get_all_user,
            methods=["GET"],
        )

        # Get a user by telegram_id
        app.add_url_rule(
            "/api/auth/<int:telegram_id>",
            view_func=cls(user_service).get_by_telegram_id,
            methods=["GET"],
        )

        # delete a user record by telegram_id
        app.add_url_rule(
            "/api/auth/<int:telegram_id>",
            view_func=cls(user_service).delete_by_telegram_id,
            methods=["DELETE"],
        )
        
        # delete all user records
        app.add_url_rule(
            "/api/auth/",
            view_func=cls(user_service).delete_all_user,
            methods=["DELETE"],
        )
                
        # add a user record
        app.add_url_rule(
            "/api/auth/<int:telegram_id>",
            view_func=cls(user_service).update_user_username,
            methods=["PUT"],
        )