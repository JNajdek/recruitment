"""
@author Jakub Najdek
@version 1.0
"""
import unittest
import requests
import json


class ApiProperValuesTest(unittest.TestCase):
    def setUp(self):
        # Resetting the database after each test so tests are independent
        requests.delete("http://127.0.0.1:5000/restart")
        # Assert cars with proper values
        self.car1_data = {
            "make": "Honda",
            "model": "Accord"
        }
        self.car2_data = {
            "make": "Honda",
            "model": "Civic"
        }
        self.car3_data = {
            "make": "Honda",
            "model": "Pilot"
        }
        self.car4_data = {
            "make": "Honda",
            "model": "Fit"
        }
        self.car5_data = {
            "make": "Honda",
            "model": "Shadow"
        }

    def add_cars(self):
        # Testing  POST/cars endpoint
        requests.post("http://127.0.0.1:5000/cars", json=self.car1_data)
        requests.post("http://127.0.0.1:5000/cars", json=self.car2_data)
        requests.post("http://127.0.0.1:5000/cars", json=self.car3_data)
        requests.post("http://127.0.0.1:5000/cars", json=self.car4_data)
        requests.post("http://127.0.0.1:5000/cars", json=self.car5_data)

    def rate_cars(self):
        requests.get("http://127.0.0.1:5000/cars")
        car_tmp = self.car1_data.copy()
        car_tmp["rate"] = 2
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)

        car_tmp = self.car2_data.copy()
        car_tmp["rate"] = 2
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)
        car_tmp["rate"] = 3
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)

        car_tmp = self.car3_data.copy()
        car_tmp["rate"] = 3
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)
        car_tmp["rate"] = 2
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)
        car_tmp["rate"] = 1
        requests.post("http://127.0.0.1:5000/rate", json=car_tmp)

    def test_post_cars(self):
        # Adding cars to an api's database
        self.add_cars()
        # Reading added data from database
        response = requests.get("http://127.0.0.1:5000/cars")
        # Loading exemplary answer from json file
        with open('answers1.json') as f:
            answer1 = json.load(f)
        # Testing POST/cars endpoint by comparing API's response with exemplary answer
        self.assertEqual(response.json(), answer1)

    def test_post_rate(self):
        # Adding cars to an api's database
        self.add_cars()
        # Adding rates to cars in api's database
        self.rate_cars()
        response = requests.get("http://127.0.0.1:5000/cars")
        # Testing POST/rate endpoint by comparing API's response with manually calculated average rate and a
        # number of rates for each car in a database
        self.assertAlmostEqual(response.json()[0]["avg_rate"], 2 / 1)
        self.assertAlmostEqual(response.json()[0]["number_of_rates"], 1)
        self.assertAlmostEqual(response.json()[1]["avg_rate"], (2 + 3) / 2)
        self.assertAlmostEqual(response.json()[1]["number_of_rates"], 2)
        self.assertAlmostEqual(response.json()[2]["avg_rate"], (1 + 2 + 3) / 3)
        self.assertAlmostEqual(response.json()[2]["number_of_rates"], 3)
        # POST/rate doesn't change any more keys

    def test_get_popular(self):
        # Adding cars and rates to an api's database
        self.add_cars()
        self.rate_cars()
        # Requesting top 3 most popular cars in API's database
        response = requests.get("http://127.0.0.1:5000/popular")
        # Loading exemplary answer from json file
        with open('answers2.json') as f:
            answer2 = json.load(f)
        # Testing GET/popular endpoint by comparing API's response with exemplary answer
        self.assertEqual(response.json(), answer2)

    def tearDown(self):
        # Resetting the database after each test so tests are independent
        requests.delete("http://127.0.0.1:5000/restart")


class ApiImproperValuesTest(unittest.TestCase):
    # POST/cars endpoint
    def test_improper_car_types1(self):
        # Testing if request to add a car with improper data type will raise correct error

        # car1 is a string
        car1 = "Honda CrossTour"
        response1 = requests.post("http://127.0.0.1:5000/cars", json=car1)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response1.text, '{\n  "error": "Invalid key"\n}\n')
        self.assertEqual(response1.status_code, 400)
        # car2 is a dictionary by with an incorrect key
        car2 = {
            "make": "Honda",
            "incorrect key": "del Sol"
        }
        requests.post("http://127.0.0.1:5000/cars", json=car2)
        response2 = requests.post("http://127.0.0.1:5000/cars", json=car1)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response2.text, '{\n  "error": "Invalid key"\n}\n')
        self.assertEqual(response2.status_code, 400)

    def test_car_out_of_vpic_database1(self):
        # Creating a car which is not in vpic database(outside database not API's)
        car = {
            "make": "Jaguar",
            "model": "Pilot"
        }
        # Attempting to add that car to API's database
        response = requests.post("http://127.0.0.1:5000/cars", json=car)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response.json()["error"], "Not found")
        self.assertEqual(response.status_code, 404)




    # POST/rate endpoint
    def test_improper_car_types2(self):
        # Creating cars with wrong type and key
        car1 = "Honda CrossTour 3"
        requests.post("http://127.0.0.1:5000/cars", json=car1)
        car2 = {
            "make": "Honda",
            "incorrect": "Civic",
            "rate": 3
        }
        # Attempting to rate that car
        requests.post("http://127.0.0.1:5000/cars", json=car2)
        response = requests.post("http://127.0.0.1:5000/rate", json=car2)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response.json()["error"], "Invalid key")
        self.assertEqual(response.status_code, 400)

    def test_car_out_of_api_database(self):
        # Creating a correct car but not in API's database
        car = {
            "make": "Jaguar",
            "model": "XF",
            "rate": 3
        }
        # Attempting to rate that car
        response = requests.post("http://127.0.0.1:5000/rate", json=car)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response.json()["error"], "Not found")
        self.assertEqual(response.status_code, 404)

    def test_improper_rate(self):
        # Creating a car with correct type and keys and adding that car to a database
        car = {
            "make": "Honda",
            "model": "Pilot"
        }
        # Rating that car using incorrect rate
        requests.post("http://127.0.0.1:5000/car", json=car)
        # Rate out of an 1-5 range
        car["rate"] = 7
        response9 = requests.post("http://127.0.0.1:5000/rate", json=car)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response9.json()["error"], "Invalid value")
        self.assertEqual(response9.status_code, 400)
        # Rate is not an int
        car["rate"] = 3.3
        response = requests.post("http://127.0.0.1:5000/rate", json=car)
        # Testing if correct error is raised and right code is returned
        self.assertEqual(response.json()["error"], "Invalid value")
        self.assertEqual(response.status_code, 400)
