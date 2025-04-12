from flask.views import MethodView
from flask import jsonify
from flask import request
from flask import session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging
 
logger = logging.getLogger(__name__)
 
 
class CrushController(MethodView):
    def __init__(self, crush_service):
        self._crush_service = crush_service

    def add_crush(self):
        logger.info("Handling POST > add")
        data = request.get_json()

        # Extract and validate data from the request JSON
        try:
            telegram_id = str(data['telegram_id'])
            crush_user_id = str(data['crush_user_id'])

            if len(telegram_id) != 10 or len(crush_user_id) != 10:
                raise ValueError("Invalid telegram_id and crush_user_id (Must be 10 digits)")

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
            db_result = self._crush_service.insert_crush(
                telegram_id, crush_user_id 
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
    
    def get_all_telegram_id(self):
        logger.info("Handling GET > get all user")

        try:
            entries = self._crush_service.get_all_telegram_id()
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
    
    def get_by_user_telegram_id(self, telegram_id):
        logger.info(f"Handling GET > get user by ID: {telegram_id}")

        try:
            user = self._crush_service.get_by_user_telegram_id(telegram_id)
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
        
    def get_by_crush_user_id(self, crush_user_id):
        logger.info(f"Handling GET > get user by ID: {crush_user_id}")

        try:
            user = self._crush_service.get_by_crush_user_id(crush_user_id)
            if user:
                return jsonify({"success": True, "data": user}), 200
            else:
                return (
                    jsonify(
                        {"success": False, "message": f"No user found with ID {crush_user_id}"}
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
        
    def delete_by_user_telegram_id(self, telegram_id):
        logger.info("Handling DELETE > delete by some telegram_id")
 
        try:
            result = self._crush_service.delete_by_telegram_id(telegram_id)
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
        
    def delete_all_crushes(self):
        logger.info("Handling DELETE > delete all")
        try:
            num_deleted = self._crush_service.delete_all_crushes()
 
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
        
    def update_user_crush(self, telegram_id):
        logger.info("Handling PUT > update crush")
        data = request.get_json()

        # Extract and validate data from the request JSON
        try:
            new_crush = str(data['new_crush_user_id'])
            result = self._crush_service.update_crush(telegram_id, new_crush)
            if result:
                return jsonify({"success": True, "message": f"crush updated successfully to {new_crush}"}), 200
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
            "/api/auth/crush/",
            view_func=cls(user_service).add_crush,
            methods=["POST"],
        )

        # get all user records
        app.add_url_rule(
            "/api/auth/crush/",
            view_func=cls(user_service).get_all_telegram_id,
            methods=["GET"],
        )

        # Get a user by telegram_id
        app.add_url_rule(
            "/api/auth/crush/<int:telegram_id>",
            view_func=cls(user_service).get_by_user_telegram_id,
            methods=["GET"],
        )   
        
        # Get a user by crush_user_id
        app.add_url_rule(
            "/api/auth/crush/crush_user_id/<int:crush_user_id>",
            view_func=cls(user_service).get_by_crush_user_id,
            methods=["GET"],
        )

        # delete a crush record by telegram_id
        app.add_url_rule(
            "/api/auth/crush/<int:telegram_id>",
            view_func=cls(user_service).delete_by_user_telegram_id,
            methods=["DELETE"],
        )
        
        # delete all crush records
        app.add_url_rule(
            "/api/auth/crush/",
            view_func=cls(user_service).delete_all_crushes,
            methods=["DELETE"],
        )
                
        # update a crush record
        app.add_url_rule(
            "/api/auth/crush/<int:telegram_id>",
            view_func=cls(user_service).update_user_crush,
            methods=["PUT"],
        )