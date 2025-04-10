from .services.database_utility import DatabaseUtility

import logging
 
logger = logging.getLogger(__name__)
 
 
class MainController:
    def __init__(self, app):
        # Keep track of whether routes have been set up
        self._is_routes_set_up = False
 
        self._app = app

        # Initialize other attributes to None, they'll be set up later
        self._database_utility = DatabaseUtility(self._app)
        self._db = self._database_utility.db

        self._prediction_history_service = None
    @property
    def db(self):
        return self._db

    @property
    def database_utility(self):
        return self._database_utility
    
    def _setup_routes(self):
        """
        Configure and register API routes for the Flask application.
 
        The method uses Flask's add_url_rule to register these routes, utilizing MethodView
        classes for handling the requests.
 
        Note:
        - This method should be called after the AI model and prediction history service have been initialized.
        - The controllers are imported within this method to avoid circular imports.
 
        Raises:
            ImportError: If the required controllers cannot be imported.
        """
        # Check if routes are already set up
        if self._is_routes_set_up:
            logger.info("Warning: Routes are already set up. Skipping.")
            return
 
        # Register the routes
        from .controllers.default_controller import DefaultController
        DefaultController.register(self._app)
 
        # from .controllers.user_controller import UserController
        # UserController.register(self._app, self._user_service)

        # Mark routes as set up
        self._is_routes_set_up = True
 
    def run(self):
        # The AI Model is a very important part of the application.
        # If the AI model is not loaded, the application will not function properly,
        # And the return statement ensures that the application will not start.
        
        self._database_utility.init(self._app)

        # Set up the user service.
        # from .services.user_service import UserInfoService
        # self._user_service = UserInfoService(self._database_utility)

        # Register the blueprint.
        self._setup_routes()
        