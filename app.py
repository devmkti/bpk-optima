import numpy as np
import pandas as pd
import pulp
from scipy.optimize import minimize, Bounds, LinearConstraint
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def base():
  return render_template("home.html")

@app.route("/home")
def home():
  return render_template("home.html")

@app.route("/addNewProject")
def addNewProject():
  return render_template("add-new-project.html")

@app.route("/listOfProject")
def listOfProject():
  return render_template("list-of-project.html")

@app.route("/calculateBWM", methods=['POST'])
def calculate():

@app.route("/calculateBWMBayesian", methods=['POST'])
def calculate():

if __name__ == "__main__":
    app.run(debug=True)
