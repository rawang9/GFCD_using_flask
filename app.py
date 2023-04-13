from my_website import app
from my_website.customer import views


if __name__ == "__main__":
    app.logger.debug("Running app now")
    app.run(debug=True)