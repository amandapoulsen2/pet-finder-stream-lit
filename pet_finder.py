import streamlit as st
import requests
from datetime import date, timedelta, datetime
import pandas as pd
import os
from geopy.geocoders import Nominatim
import random
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Constants
api_key = os.environ["PET_FINDER_API_KEY"]
secret = os.environ["PET_FINDER_API_SECRET"]
ttl = 3600
days_to_subtract = 7
limit = 50

# Services
gn = Nominatim(user_agent="myapp")


# Methods
@st.cache_data
def generate_geo_from(location):
    return gn.geocode(f"{location} USA")


@st.cache_data
def animal_to_location(animal):
    min = -0.01000
    max = 0.01000
    contact = animal["contact"]
    address = contact["address"]
    location = generate_geo_from(f"{address['city']} {address['postcode']}")
    lat_delta = random.uniform(min, max)
    lon_delta = random.uniform(min, max)

    latitude = None
    longitude = None
    if location is not None:
        latitude = location.latitude + lat_delta
        longitude = location.longitude + lon_delta

    return {
        "latitude": latitude,
        "longitude": longitude,
        "name": animal["name"],
    }


@st.cache_data
def map_creator_from_locations(locations, latitude, longitude):
    from streamlit_folium import folium_static
    import folium

    # TODO learn how to make the map based on city
    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # TODO learn how to add markers to map
    # add marker for the station
    for location in locations:
        latitude_loc = location["latitude"]
        longitude_loc = location["longitude"]

        if latitude_loc is not None and longitude_loc is not None:
            folium.Marker(
                [latitude_loc, longitude_loc],
                popup=location["name"],
                tooltip=location["name"],
            ).add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)


@st.cache_data
def map_creator(latitude, longitude):
    from streamlit_folium import folium_static
    import folium

    # TODO learn how to make the map based on city
    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # TODO learn how to add markers to map
    # add marker for the station
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)


def build_headers_with_token():
    token = get_token()
    return {"Authorization": "Bearer " + token}


# https://www.petfinder.com/developers/v2/docs/#using-the-api
@st.cache_data(ttl=ttl)
def get_token():
    token_url = f"https://api.petfinder.com/v2/oauth2/token"
    body = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret,
    }
    response = requests.post(token_url, json=body).json()
    # st.write(response)
    return response["access_token"]


# https://www.petfinder.com/developers/v2/docs/#get-animal-types
@st.cache_data(ttl=ttl)
def get_animal_type(animal):
    headers = build_headers_with_token()
    url = f"https://api.petfinder.com/v2/types/{animal}"
    response = requests.get(url, headers=headers).json()
    return response


# https://www.petfinder.com/developers/v2/docs/#get-animals
@st.cache_data(ttl=ttl)
def get_animals_by_location(location, distance, type, gender, color, coat, after):
    headers = build_headers_with_token()
    page = 1
    url = f"https://api.petfinder.com/v2/animals"

    params = {
        "location": location,
        "distance": distance,
        "type": type,
        "gender": gender,
        "color": color,
        "coat": coat,
        "page": page,
        "limit": limit,
    }

    response = requests.get(url=url, params=params, headers=headers).json()
    return response


def generate_gender_lists(animals):
    males = 0
    females = 0

    for animal in animals:
        gender = animal["gender"]
        if gender == "Male" or gender == "male":
            males = males + 1
        else:
            females = females + 1

    return [males, females]


def generate_coats_lists(animals, coats):
    feq = [0] * len(coats)
    # males = [0] * len(coats)
    # females = [0] * len(coats)

    for animal in animals:
        coat = animal["coat"]
        index = coats.index(coat)
        feq[index] = feq[index] + 1

    return feq


def generate_animal_for_df(animals):
    mapped_animals = []

    for animal in animals:
        id = animal["id"]
        organization_id = animal["organization_id"]
        name = animal["name"]
        age = animal["age"]
        gender = animal["gender"]
        size = animal["size"]
        coat = animal["coat"]

        breed_primary = None
        breed_secondary = None
        breed = animal["breeds"]
        if breed is not None:
            breed_primary = breed["primary"]
            breed_secondary = breed["secondary"]

        color_primary = None
        color_secondary = None
        color = animal["colors"]
        if color is not None:
            color_primary = color["primary"]
            color_secondary = color["secondary"]

        city = None
        state = None
        postcode = None
        contact = animal["contact"]
        if contact is not None:
            address = contact["address"]
            if address is not None:
                city = address["city"]
                state = address["state"]
                postcode = address["postcode"]

        mapped_animal = {
            "Id": id,
            "Organization Id": organization_id,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Size": size,
            "Coat": coat,
            "Breed (primary)": breed_primary,
            "Breed (secondary)": breed_secondary,
            "Color (Primary)": color_primary,
            "Color (Secondary)": color_secondary,
            "City": city,
            "State": state,
            "Postcode": postcode,
        }

        mapped_animals.append(mapped_animal)

    return mapped_animals


# State
default_animal_type = "Cat"
animal_type_data = get_animal_type(default_animal_type)["type"]
default_coats = animal_type_data["coats"]
default_colors = animal_type_data["colors"]

dog_type_data = get_animal_type("Dog")["type"]
dog_default_coats = animal_type_data["coats"]
dog_default_colors = animal_type_data["colors"]

if st.session_state.get("clear"):
    st.session_state["name"] = ""
    st.session_state["zip"] = 90210
    st.session_state["distance_from_zip"] = 20
    st.session_state["animal_type"] = default_animal_type
    # st.session_state["selected_coats"] = default_coats
    # st.session_state["selected_colors"] = default_colors

# Requirements
st.markdown(
    "<h1 style='text-align: center;'>Pet Finder API</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h2 style='text-align: center;'>Streamlit and Pet Finder API</h2>",
    unsafe_allow_html=True,
)

st.divider()

# Columns
col1, col2 = st.columns(2, gap="Medium")

# - Radio Button: cat or dog
animal_type = col1.radio(
    "Please select a type of pet:", ["Cat", "Dog"], key="animal_type"
)

# - Number input for zip
zip = col1.number_input(
    "Zip Code, e.g. 90210", key="zip", min_value=30001, max_value=99999, value=90210
)

# - Select-slider: distance from zip
default_distance = 20
distance_from_zip = col1.slider(
    "Distance (miles) from zip:", 5, 100, default_distance, key="distance_from_zip"
)

# - Date/Time input: filter results by `status_changed_at`?
default_filter_date = date.today() - timedelta(days=days_to_subtract)
filter_date = col1.date_input(
    label="Only show results updated after",
    value=default_filter_date,
    format="MM/DD/YYYY",
    key="filter_date",
)

fitler_date_string = f"{filter_date}"

if fitler_date_string is not None:
    if isinstance(fitler_date_string, str):
        try:
            after_date = datetime.strptime(fitler_date_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            after_date = datetime.strptime(fitler_date_string, "%Y-%m-%d")
        fitler_date_string = after_date.astimezone().replace(microsecond=0).isoformat()

# - Checkbox for genders
male_cb = col1.checkbox("Male", value=True)
female_cb = col1.checkbox("Female", value=True)

genders = ""

if male_cb and female_cb:
    genders = "Male,Female"
elif male_cb and not female_cb:
    genders = "Male"
elif female_cb and not male_cb:
    genders = "Female"


# - Multiselect for [types data](https://api.petfinder.com/v2/types/{animal})
# if animal_type is "Dog":
#     selected_coats = col1.multiselect(
#         "Please select coat(s):",
#         dog_default_coats,
#         dog_default_coats,
#         key="selected_coats",
#     )
#     selected_colors = col1.multiselect(
#         "Please select color(s):",
#         dog_default_colors,
#         dog_default_colors,
#         key="selected_colors",
#     )
# else:
#     selected_coats = col1.multiselect(
#         "Please select coat(s):", default_coats, default_coats, key="selected_coats"
#     )
#     selected_colors = col1.multiselect(
#         "Please select color(s):", default_colors, default_colors, key="selected_colors"
#     )

selected_coats = col1.multiselect(
    "Please select coat(s):", default_coats, default_coats, key="selected_coats"
)

# Map selected values
selected_coats_string = ",".join(selected_coats)
# selected_colors_string = ",".join(selected_colors)

# - Button to reset filters
col1.button("Reset", key="clear", type="primary")

# Get animals
animals_by_location = get_animals_by_location(
    zip,
    distance_from_zip,
    animal_type,
    genders,
    "",  # selected_colors_string,
    selected_coats_string,
    fitler_date_string,
)

if "status" in animals_by_location and animals_by_location["status"] >= 400:
    col2.error(f"Unable to find animals for given location: '{zip}'", icon="🚨")
else:
    animals = animals_by_location["animals"]

    animal_locations = []

    for animal in animals:
        animal_locations.append(animal_to_location(animal))

    # - Display results on map
    location_from_zip = generate_geo_from(zip)
    if location_from_zip is None:
        # - Error box
        col2.error(f"Could not generate the map given '{zip}'", icon="🚨")
    else:
        # - Info box
        col2.info(f"Generating map for {location_from_zip}", icon="ℹ️")
        with col2:
            map_creator_from_locations(
                animal_locations,
                location_from_zip.latitude,
                location_from_zip.longitude,
            )

    st.divider()

    col3, col4 = st.columns(2)

    # - PyPlot -- breed and gender
    with col3:
        col3.markdown(
            "<h2 style='text-align: center;'>Frequency of Males vs Females</h2>",
            unsafe_allow_html=True,
        )
        gender_list = generate_gender_lists(animals=animals)
        fig, ax = plt.subplots()
        bar_colors = ["tab:red", "tab:blue"]
        ax.bar(["Male", "Female"], gender_list, color=bar_colors)
        ax.set_ylabel("Gender Count")
        ax.set_title("Males vs Females")
        st.pyplot(fig)

        # selected_coats = default_coats
        # if animal_type is "Dog":
        #     selected_coats = dog_default_coats

    with col4:
        col4.markdown(
            "<h2 style='text-align: center;'>Frequency of Coat(s)</h2>",
            unsafe_allow_html=True,
        )
        coat_list = generate_coats_lists(animals=animals, coats=selected_coats)
        fig2, ax2 = plt.subplots()
        # If there's more than 4 categories, the values will wrap
        bar_colors2 = ["tab:red", "tab:blue", "tab:green", "tab:orange"]
        ax2.bar(selected_coats, coat_list, color=bar_colors2)
        ax2.set_ylabel("Coat Count")
        ax2.set_title("Fequency of Coats")
        st.pyplot(fig2)

    st.divider()

    # - Interactive Table for Results
    mapped_animals = generate_animal_for_df(animals=animals)

    df = pd.DataFrame(
        mapped_animals,
        columns=[
            "Id",
            "Organization Id",
            "Name",
            "Age",
            "Gender",
            "Size",
            "Coat",
            "Breed (primary)",
            "Breed (secondary)",
            "Color (Primary)",
            "Color (Secondary)",
            "City",
            "State",
            "Postcode",
        ],
    )
    df.index += 1
    st.markdown(
        "<h2 style='text-align: center;'>Results in Interactive Table</h2>",
        unsafe_allow_html=True,
    )
    st.dataframe(df)
