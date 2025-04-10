from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
 
logger = logging.getLogger(__name__)
 
 
class DatabaseUtility:
    def __init__(self, app):
        # TODO: Uncomment this for remote db
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # ca_cert_path = os.path.join(current_dir, "..", "ca.pem")
 
        # # Set SQLAlchemy configs
        # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        #     "connect_args": {"ssl_ca": ca_cert_path, "ssl_verify_cert": True}
        # }
 
        self._db = SQLAlchemy(app)
 
    def init(self, app):
        # Import the models for create_all() to work correctly.
        # This is essential and important.
        from .models import UserInfo
 
        # Check if the database exists, create it if it doesn't.
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
 
        # Use the app context to create all database tables.
        with app.app_context():
            self._db.create_all()
            self._db.session.commit()
            print("Database tables created!")
 
    @property
    def db(self):
        return self._db
 
    @contextmanager
    def session_scope(self):
        """
        The context manager in DatabaseUtility is a powerful tool for
        managing database sessions. It's implemented using the @contextmanager
        decorator and the session_scope method. Here's how it works:
 
        1.  When you use the "with" statement with session_scope,
            it creates a new database session.
 
        2.  The "yield session" line temporarily exits the context manager and
            allows the code inside the "with" block to execute, using the created session.
 
        3.  If the code inside the "with" block completes without raising an exception,
            the context manager resumes after the "yield" and calls session.commit(),
            saving all changes to the database.
 
        4.  If an exception occurs, it's caught in the "except" block.
            The session.rollback() is called, undoing any changes made during the session,
            preventing partial updates.
 
        5.  Whether an exception occurred or not, the "finally" block ensures
            session.close() is always called, releasing database resources.
 
        6.  If an exception was caught, it's re-raised after the session is closed,
            allowing the calling code to handle it.
 
        This design ensures proper resource management, consistent transaction handling,
        and clean error propagation. It simplifies database operations by centralizing
        session management and error handling, making the code using the database more
        concise and less prone to resource leaks or inconsistent states.
        """
        session = self._db.session
 
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            session.close()
 
    def get_session(self):
        return self._db.session