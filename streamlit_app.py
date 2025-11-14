import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
# Title and instructions
st.title(":cup_with_straw: Customize your smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your smoothie and give your smoothie a name")

# Name input for smoothie
smoothie_name = st.text_input("Name on Smoothie")
if smoothie_name:
    st.write("The name on your smoothie will be:", smoothie_name)

# Snowflake session and fruit options
cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
st.dataframe(data=my_dataframe,use_container_width=True)
st.stop()

# Convert Snowpark DataFrame to simple Python list
fruit_names = [row.FRUIT_NAME for row in my_dataframe.select("FRUIT_NAME").collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_names
)

# Submit button
submit_button = st.button("Submit Order")

if submit_button:
    if ingredients_list and smoothie_name:
        # Convert list to string
        ingredients_string = ""
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            st.subheader(fruit_chosen + 'Nutrition Information ')
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
            sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

        # Build SQL insert statement
        my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                            VALUES ('""" + ingredients_string + """', '""" + smoothie_name + """')"""

        # Execute insert in Snowflake
        session.sql(my_insert_stmt).collect()

        # Display success message and selected ingredients
        st.success(f"Your Smoothie is ordered, {smoothie_name}!", icon="✅")
        st.write("You selected these ingredients:")
        st.write(ingredients_list)

    else:
        st.write("Please select at least one ingredient and enter your name before submitting.")


smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
