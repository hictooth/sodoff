import os

from flask import Flask


def create_app():
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'sodoff.sqlite'),
  )

  # ensure the instance folder exists
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  # the simple health check endpoint
  @app.route('/health-check')
  def health_check():
    return 'OK'

  # init the db
  from . import db
  db.init_app(app)

  # register the api endpoints
  from .api import bp as api
  app.register_blueprint(api)

  return app
