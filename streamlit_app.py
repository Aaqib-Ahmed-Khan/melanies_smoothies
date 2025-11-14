import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title(":cup_with_straw: Customize your smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your smoothie and give your smoothie a name")

# Name input for smoothie
smoothie_name = st.text_input("Name on Smoothie")
if smoothie_name:
    st.write("The name on your smoothie will be:", smoothie_name)

# Snowflake session and fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Convert to list for multiselect
fruit_names = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_names
)

# Submit button
submit_button = st.button("Submit Order")

if submit_button:
    if ingredients_list and smoothie_name:
        ingredients_string = ""
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for', fruit_chosen, 'is', search_on)

        # Build SQL insert statement
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{smoothie_name}')
        """
        session.sql(my_insert_stmt).collect()

        st.success(f"Your Smoothie is ordered, {smoothie_name}!", icon="✅")
        st.write("You selected these ingredients:")
        st.write(ingredients_list)
    else:
        st.write("Please select at least one ingredient and enter your name before submitting.")
