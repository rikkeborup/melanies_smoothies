import streamlit as st
import requests
from snowflake.snowpark.functions import col

def clear_multi():
    st.session_state.multiselect = []
    return

def clear_text():
    st.session_state["name_on_order_text"] = ''
    
def insert_sql(insert_stmt, name_on_order):
    session.sql(insert_stmt).collect()
    st.success('Your Smoothie is ordered '+name_on_order+'!', icon="✅")
    return

def insert_and_clear(insert_stmt, name_on_order):
    insert_sql(insert_stmt,name_on_order)
    clear_multi()
    clear_text()

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input('Name on smoothie:', key='name_on_order_text')
st.write('The name on your smoothie will be:', name_on_order)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect('Choose up to 5 ingredients:', 
                                  my_dataframe, 
                                  key="multiselect",
                                  max_selections=5)

if ingredients_list:
    
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon" + lower(fruit_chosen))
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order) values ('""" + ingredients_string + """','"""+name_on_order+"""' )"""

    st.button('Submit Order', on_click=lambda: insert_and_clear(my_insert_stmt, name_on_order))
