import random
import pickle
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.pipeline import Pipeline
from typing import List, Optional

# Class for managing parameters
class Params:
    def __init__(self, n_neighbors=6, return_distance=False):
        self.n_neighbors = n_neighbors
        self.return_distance = return_distance

# Class for prediction input validation and management
class PredictionIn:
    def __init__(self, nutrition_input: List[float], params: Optional[Params] = None):
        self.nutrition_input = self.validate_nutrition_input(nutrition_input)
        self.params = params or Params()

    @staticmethod
    def validate_nutrition_input(value: List[float]) -> List[float]:
        if len(value) != 9:
            raise ValueError("nutrition_input must contain exactly 9 elements.")
        return value

# Class for representing recipes
class Recipe:
    def __init__(self, **kwargs):
        self.Name = kwargs.get("Name", "")
        self.CookTime = kwargs.get("CookTime", "")
        self.PrepTime = kwargs.get("PrepTime", "")
        self.TotalTime = kwargs.get("TotalTime", "")
        self.RecipeIngredientParts = kwargs.get("RecipeIngredientParts", [])
        self.Calories = kwargs.get("Calories", 0.0)
        self.FatContent = kwargs.get("FatContent", 0.0)
        self.SaturatedFatContent = kwargs.get("SaturatedFatContent", 0.0)
        self.CholesterolContent = kwargs.get("CholesterolContent", 0.0)
        self.SodiumContent = kwargs.get("SodiumContent", 0.0)
        self.CarbohydrateContent = kwargs.get("CarbohydrateContent", 0.0)
        self.FiberContent = kwargs.get("FiberContent", 0.0)
        self.SugarContent = kwargs.get("SugarContent", 0.0)
        self.ProteinContent = kwargs.get("ProteinContent", 0.0)
        self.RecipeInstructions = kwargs.get("RecipeInstructions", [])
        self.image_link = kwargs.get("Images", "")

# Function to scale data
def scaling(dataframe):
    scaler = StandardScaler()
    try:
        numeric_data = dataframe.iloc[:, 6:15].apply(pd.to_numeric, errors='coerce').fillna(0)
        prep_data = scaler.fit_transform(numeric_data)
        return prep_data, scaler
    except Exception as e:
        print(f"Error during scaling: {e}")
        raise ValueError("Ensure that the dataframe contains numeric nutritional columns from index 6 to 15.")

# Function to train and save the model
def train_and_save_model():
    try:
        # Load dataset
        dataset = pd.read_csv('dataset.csv')
        
        # Scale the data
        prep_data, scaler = scaling(dataset)
        
        # Train Nearest Neighbors Model
        neigh = NearestNeighbors(metric='cosine', algorithm='brute')
        neigh.fit(prep_data)

        # Save Model & Scaler
        with open("trained_model.pkl", "wb") as model_file:
            pickle.dump(neigh, model_file)

        with open("scaler.pkl", "wb") as scaler_file:
            pickle.dump(scaler, scaler_file)

        print("Model and scaler saved successfully. You can now delete 'dataset.csv'.")

    except FileNotFoundError:
        print("Dataset file not found.")
    except Exception as e:
        print(f"Error: {e}")

# Function to load the trained model
def load_model():
    try:
        with open("trained_model.pkl", "rb") as model_file:
            neigh = pickle.load(model_file)

        with open("scaler.pkl", "rb") as scaler_file:
            scaler = pickle.load(scaler_file)

        return neigh, scaler

    except FileNotFoundError:
        raise FileNotFoundError("Trained model not found. Please run 'train_and_save_model()' first.")

# Function to output recommended recipes
def output_recommended_recipes(dataframe):
    if dataframe is not None:
        return dataframe.to_dict("records")
    return None

# Function to predict recipes
def predict_recipes(nutrition_input: List[float]) -> List[Recipe]:
    # Load trained model & scaler
    neigh, scaler = load_model()

    # Scale input data
    _input = np.array(nutrition_input).reshape(1, -1)
    _input = scaler.transform(_input)

    # Get recommended indices
    indices = neigh.kneighbors(_input, n_neighbors=6, return_distance=False)[0]

    # Load dataset only for retrieving recommended recipes
    dataset = pd.read_csv('dataset.csv')  
    recommended_data = dataset.iloc[indices]

    # Convert output into Recipe instances
    output = output_recommended_recipes(recommended_data)
    return [Recipe(**recipe_data) for recipe_data in output] if output else []

