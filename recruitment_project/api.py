"""
@author Jakub Najdek
@version 1.0
"""
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
cars = []


@app.errorhandler(NameError)
def handle_name_error(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(KeyError)
def handle_key_error(error):
    return jsonify({"error": "Invalid key"}), 400


@app.errorhandler(ValueError)
def handle_key_error(error):
    return jsonify({"error": "Invalid value"}), 400


@app.route("/cars")
def get_cars():
    """
    Retrieves list of cars saved in the API's database and their parameters
    :return: json response with a list of dictionaries and a code informing user the operation was a success
    """
    return jsonify(cars), 200


@app.route("/popular", methods=["GET"])
def get_top3_popular_cars():
    """
    Retrieves list of 3 cars with the biggest amount of rates.
    :return: json response with a list of 3 dictionaries and a code informing user the operation was a success
    """
    cars_copy = cars.copy()
    popularity = lambda cars_copy: cars_copy["number_of_rates"]
    cars_copy.sort(reverse=True, key=popularity)
    if len(cars) <= 3:
        return jsonify(cars_copy), 200

    top3 = cars_copy[:3]

    return jsonify(top3), 200


@app.route("/cars", methods=["POST"])
def create_car():
    """
    Expands database by adding a new car resource. Added car must be a dictionary containing
    'make' and 'model' keys
    :return: A string containing a success message and a code informing about properly creating new resource
    """
    data = request.get_json()
    if "model" and "make" in data:
        for car in cars:
            if car["model"] == data["model"] and car["make"] == data["make"]:
                raise ValueError("Car already exist in a database")

        make_data = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json")
        make_data_json = make_data.json()
        makes = []
        for car in make_data_json["Results"]:
            makes.append(car["MakeName"])

        if data["make"].upper() in makes:
            make = data["make"]
            model_data = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/{make}?format=json")
            model_data_json = model_data.json()
            models = []

            for car in model_data_json["Results"]:
                models.append(car["Model_Name"])

            if data["model"] in models:
                cars.append(data)
                cars[-1]["number_of_rates"] = 0
                return "The resource has been successfully added", 201
            else:
                raise NameError("That model doesn't exist")
        else:
            raise NameError("That make doesn't exist")
    else:
        raise KeyError("The request must contain a dictionary with a 'make' and a 'model' keys")


@app.route("/rate", methods=["POST"])
def rate_car():
    """
    Rates a car in the database and updates its average rate. Rated car must be a dictionary containing
    'make', 'model' and 'rate' keys
    :return: A string containing a success message and a code informing about properly creating new rate
    """
    data = request.get_json()
    if "rate" and "make" and "model" in data:
        rate = data["rate"]
        make = data["make"]
        model = data["model"]

        if isinstance(rate, int) and rate >= 1 and rate <= 5:
            for car in cars:
                if car["make"] == make and car["model"] == model:
                    index = cars.index(car)
                    old_number_of_rates = cars[index]["number_of_rates"]
                    cars[index]["number_of_rates"] = old_number_of_rates + 1
                    if "avg_rate" in cars[index]:  # sprawdza czy jest pole avg_rate jak nie to je tworzy
                        cars[index]["avg_rate"] = (cars[index]["avg_rate"] * old_number_of_rates + rate) / cars[index][
                            "number_of_rates"]
                    # first rate
                    else:
                        cars[index]["avg_rate"] = rate
                    return "The car has been successfully rated", 201
            raise NameError("That car doesn't exist in our database")
        else:
            raise ValueError("Rate must be a number between 1-5")
    else:
        raise KeyError("The request must contain a dictionary with a 'make', a 'model' and a 'rate' keys")


@app.route("/restart", methods=["DELETE"])
def restart_database():
    """
    Clears the cars list and restarts the database
    :return: A string containing information that the operation was a success and a code informing about properly
     clearing the database
    """
    cars.clear()
    return "Restarting database was a success", 204


if __name__ == "__main__":
    app.run(debug=True)
