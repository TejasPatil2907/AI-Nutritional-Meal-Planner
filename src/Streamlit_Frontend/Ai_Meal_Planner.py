import streamlit as st
from Login import display_authentication_page  
st.set_page_config(page_title="Ai Nutritional Meal Planner", page_icon="Logo.jpeg", layout="wide")
# Check if the user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    # If not logged in, show the login or signup page
    display_authentication_page()
else:
    import random
    import numpy as np
    import streamlit as st
    import pandas as pd
    from typing import List, Optional
    from Generate_Recommendations import Recipe, predict_recipes, Params
    from ImageFinder.ImageFinder import get_images_links  # Import from the backend script
    import bcrypt
    

    nutritions_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                        'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
    st.title("🌟 Ai Nutritional Meal Planner 🍕")
    if 'person' not in st.session_state:
        st.session_state.generated = False
        st.session_state.recommendations = None
        st.session_state.person = None
        st.session_state.weight_loss_option = None

    class Person:
        def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
            self.age = age
            self.height = height
            self.weight = weight
            self.gender = gender
            self.activity = activity
            self.meals_calories_perc = meals_calories_perc
            self.weight_loss = weight_loss

        def calculate_bmi(self):
            bmi = round(self.weight / ((self.height / 100) ** 2), 2)
            return bmi

        def display_result(self):
            bmi = self.calculate_bmi()
            bmi_string = f'{bmi} kg/m²'
            if bmi < 18.5:
                category = 'Underweight'
                color = 'Red'
            elif 18.5 <= bmi < 25:
                category = 'Normal'
                color = 'Green'
            elif 25 <= bmi < 30:
                category = 'Overweight'
                color = 'Yellow'
            else:
                category = 'Obesity'
                color = 'Red'
            return bmi_string, category, color

        def calculate_bmr(self):
            if self.gender == 'Male':
                bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
            else:
                bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
            return bmr

        def calories_calculator(self):
            activities = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
            weights = [1.2, 1.375, 1.55, 1.725, 1.9]
            activity_factor = weights[activities.index(self.activity)]
            maintain_calories = self.calculate_bmr() * activity_factor
            return maintain_calories

        def calculate_breakfast_nutrition(self):
            total_calories = self.weight_loss * self.calories_calculator() * self.meals_calories_perc['breakfast']
            carbs = total_calories * 0.4 / 4  # Adjust macro split
            protein = total_calories * 0.35 / 4
            fat = total_calories * 0.25 / 9
            return [total_calories, fat, 10, 300, 2000, carbs, 25, 40, protein]

        def calculate_lunch_nutrition(self):
            total_calories = self.weight_loss * self.calories_calculator() * self.meals_calories_perc['lunch']
            carbs = total_calories * 0.5 / 4  # Higher carb split
            protein = total_calories * 0.3 / 4
            fat = total_calories * 0.2 / 9
            return [total_calories, fat, 10, 300, 2000, carbs, 25, 40, protein]

        def calculate_dinner_nutrition(self):
            total_calories = self.weight_loss * self.calories_calculator() * self.meals_calories_perc['dinner']
            carbs = total_calories * 0.35 / 4  # Lower carb split
            protein = total_calories * 0.4 / 4
            fat = total_calories * 0.25 / 9
            return [total_calories, fat, 10, 300, 2000, carbs, 25, 40, protein]

        

        



    class Display:
        def __init__(self):
            self.plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
            self.weights = [1, 0.9, 0.8, 0.6]
            self.losses = ['-0 kg/week', '-0.25 kg/week', '-0.5 kg/week', '-1 kg/week']

        def display_bmi(self, person):
            st.header('BMI CALCULATOR')
            bmi_string, category, color = person.display_result()
            st.metric(label="Body Mass Index (BMI)", value=bmi_string)
            st.markdown(f"<p style='font-family:sans-serif; color:{color}; font-size: 25px;'>{category}</p>", unsafe_allow_html=True)
            st.markdown("Healthy BMI range: 18.5 kg/m² - 25 kg/m².")

        def display_calories(self, person):
            st.header('CALORIES CALCULATOR')
            maintain_calories = person.calories_calculator()
            for plan, weight, loss, col in zip(self.plans, self.weights, self.losses, st.columns(4)):
                with col:
                    st.metric(label=plan, value=f'{round(maintain_calories * weight)} Calories/day', delta=loss, delta_color="inverse")





        @staticmethod
        def display_recommendations(breakfast: List[Recipe], lunch: List[Recipe], dinner: List[Recipe]):
            st.header("🍴 Personalized Meal Plan 🌟")

            # Helper function to clean input
            def clean_input(data):
                if isinstance(data, str):
                    data = data.strip()
                    # Remove wrapping 'c(...)' if present
                    if data.startswith("c(") and data.endswith(")"):
                        data = data[2:-1]
                    return data
                return ""

            # Ensure exactly 6 recipes per section for layout consistency
            def pad_recipes(recipes, target_length=6):
                return recipes + [None] * (target_length - len(recipes))

            # Sections to display
            sections = [("Breakfast 🥞", breakfast), ("Lunch 🥗", lunch), ("Dinner 🍛", dinner)]
            for section_name, recipes in sections:
                st.subheader(section_name)

                # Ensure recipes have exactly 6 items (pad if needed)
                recipes = pad_recipes(recipes, 6)

                # Create rows of 3 columns each
                for row in range(2):  # Two rows
                    cols = st.columns(3)  # Three columns per row
                    for col, recipe in zip(cols, recipes[row * 3:(row + 1) * 3]):
                        with col:
                            if recipe is None:
                                st.write("")  # Empty cell for padding
                                continue
                            
                            # Display recipe details
                            with st.expander(f"{recipe.Name}", expanded=False):
                                # Display image
                                try:
                                    image_url = get_images_links(recipe.Name)
                                    if image_url:
                                        st.image(image_url, caption=recipe.Name, width=150)
                                    else:
                                        st.write("Image not available.")
                                except Exception as e:
                                    st.error(f"Failed to load image for {recipe.Name}: {e}")
                                    st.write("Image not available.")

                                # Display ingredients
                                st.markdown("**Ingredients:**")
                                cleaned_ingredients = clean_input(recipe.RecipeIngredientParts)
                                if cleaned_ingredients:
                                    ingredients_list = [
                                        ingredient.strip().strip('"') for ingredient in cleaned_ingredients.split(",")
                                    ]
                                    st.write("- " + "\n- ".join(ingredients_list))

                                # Display instructions
                                st.markdown("**Instructions:**")
                                cleaned_recipes = clean_input(recipe.RecipeInstructions)
                                if cleaned_recipes:
                                    instructions_list = [
                                        instruction.strip().strip('"') for instruction in cleaned_recipes.split(",")
                                    ]
                                    st.write("- " + "\n- ".join(instructions_list))



 

                
    display = Display()

    # Streamlit Form
    with st.form("recommendation_form"):
        age = st.number_input('Age', min_value=10, max_value=120, step=1)
        height = st.number_input('Height(cm)', min_value=50, max_value=300, step=1)
        weight = st.number_input('Weight(kg)', min_value=10, max_value=300, step=1)
        gender = st.radio('Gender', ('Male', 'Female'))
        activity = st.select_slider('Activity', options =['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)'])
        option = st.selectbox('Choose your weight loss plan:', display.plans)
        st.session_state.weight_loss_option = option
        weight_loss = display.weights[display.plans.index(option)]
        meals_calories_perc = {'breakfast': 0.20, 'lunch': 0.50, 'dinner': 0.33}
        generated = st.form_submit_button("Generate")


    def create_weekly_plan(breakfast_recommendations, lunch_recommendations, dinner_recommendations):
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        weekly_plan = []

        for i, day in enumerate(days_of_week):
            # Randomly assign one recipe per day for each meal
            breakfast = breakfast_recommendations[i % len(breakfast_recommendations)]
            lunch = lunch_recommendations[i % len(lunch_recommendations)]
            dinner = dinner_recommendations[i % len(dinner_recommendations)]
            
            # Format the day's entry
            weekly_plan.append({
                "Day": day,
                "Breakfast": f"{breakfast.Name} (Calories: {breakfast.Calories})",
                "Lunch": f"{lunch.Name} (Calories: {lunch.Calories})",
                "Dinner": f"{dinner.Name} (Calories: {dinner.Calories})"
            })

        # Convert to DataFrame for better display
        return pd.DataFrame(weekly_plan)




    if generated:
        st.session_state.generated = True
        person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss)
        st.session_state.person = person


        def add_noise_to_input(nutrition_input, noise_level=0.05):
            noise = np.random.uniform(-noise_level, noise_level, len(nutrition_input))
            return [max(0, ni + n) for ni, n in zip(nutrition_input, noise)]
        # Predict for each meal
        breakfast_nutrition = add_noise_to_input(person.calculate_breakfast_nutrition()) 
        lunch_nutrition = add_noise_to_input(person.calculate_lunch_nutrition())
        dinner_nutrition = add_noise_to_input(person.calculate_dinner_nutrition())


        params = Params(n_neighbors=6, return_distance=False)
        
        # Generate recommendations for each meal
        st.session_state.breakfast_recommendations = predict_recipes(breakfast_nutrition, params=params)
        st.session_state.lunch_recommendations = predict_recipes(lunch_nutrition, params=params)
        st.session_state.dinner_recommendations = predict_recipes(dinner_nutrition, params=params)

    if st.session_state.generated:
        display.display_bmi(st.session_state.person)
        display.display_calories(st.session_state.person)
        weekly_plan_df = create_weekly_plan(
            st.session_state.breakfast_recommendations,
            st.session_state.lunch_recommendations,
            st.session_state.dinner_recommendations
        )
        
        # Display the weekly table
        st.header("📅 Weekly Meal Plan ")
        st.table(weekly_plan_df)
        display.display_recommendations(
            st.session_state.breakfast_recommendations,
            st.session_state.lunch_recommendations,
            st.session_state.dinner_recommendations
        )
