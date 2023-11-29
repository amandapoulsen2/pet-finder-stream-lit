# Readme

## Build

### Commands

#### Install Requirements

```bash
python3 -m pip install -r requirements.txt
```

#### Install Streamlit

```bash
python3 -m pip install streamlit
```

## Run

### Streamlit

```bash
export PET_FINDER_API_KEY=key
export PET_FINDER_API_SECRET=secret
python3 -m streamlit run pet_finder.py
```

## Requirements

## Assignment Details

- Select a theme or topic for your web application: choose a topic that interest you -- pets
- Research and identify relevant APIs -- pet finder
- Define usability goals: Based on your selected topic, define a set of usability goals for your web app. These may include effectiveness, efficiency, learnability, memorability, error prevention, and user satisfaction
- Design the web applications: sketch out a rough layout of your application, identifying the key components and user interactions. Consider the placement of widgets, navigation elements, and data visualizations
- Develop the web app using Streamlit:
  - API requests: fetch data from the selected APIS
  - At least 1 interactive table -- st.dataframe
  - At least 2 chart elements, such as a line, area, or bar chart -- st.line_cart, st.area_chart, st.bar_chart
  - At least 1 map with points marked on it -- st.map
  - At least 1 button widget -- st.button
  - At least 1 checkbox widget -- st.checkbox
  - At least 2 essential feedback and message boxes to the users: success box, info box, warning box, error box, exception message (optional)
  - At least any 5 different widgets: radio button, select box, multiselect, slider, select-slider, text input, number input, text-area, date input, time input, file uploader, color
  - You may include a progress bar for certain components of your application; however, this not mandatory
  - You may include media elements such as image, audio or video, which are not a requirement but can add to the overall harmony of the web application being developed
  - Streamlit allows you to display a sidebar, insert containers laid out as side-by-side columns, insert a multi-element container that can be expanded/collapsed, among many other feature
- Apply HCI design principles
- Test your web app
- Document your work
- Submission

## What to Build

### Must Include

- Interactive Table for Results
- Number input for zip
- Display results on map?
- Button to reset filters
- Radio Button: cat or dog
- Multiselect for [types data](https://api.petfinder.com/v2/types)
  - Single [type](https://api.petfinder.com/v2/types/{type})
- Date/Time input: filter results by `status_changed_at`?
- Select-slider: distance from zip
- Bar chart of attributes
- Checkbox for organizations?
- Info box
- Error box

### Nice to Have

- Display photos of the animal -- not sure if the links will work
- Link to the adoption site
- Side bar
- Multi-element container
- Side-by-side columns
- Expanded/collapsed
