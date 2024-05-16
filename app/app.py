# Hi! This app was modified from another app
# Source: https://github.com/plotly/dash-world-cell-towers
# This app utilizes a similar layout to this app, with different plots / data
# I used this app to figure out how to add buttons that refresh figures
# To see the original app in production, visit: https://dash.gallery/dash-world-cell-towers/
# Originally, I used this app to host a visualization I made for a summer internship
# I repurposed this application for the Frontera Hacks inaugural hackathon
# Specifically for the Frontera Hacks A Dashboard workshop
# I've found this project to be a valuable showcase of my ability for future teams
# I hope you can gain some inspiration for it with your project / data / interests! <3

# Import libraries
import dash as dash
from dash import dcc
from dash import html
from dash import ctx
from textwrap import dedent
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import plotly.express as px

# Figure Templates
bgcolor = "#f3f3f1"  # mapbox light map land color
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

# Required line to run the app
app = dash.Dash(__name__)
server = app.server

# helper function
def get_season(trimmed_date):
    month = int(trimmed_date[0:2])
    day = int(trimmed_date[3:5])

    # Define the start day of each season
    spring_start = 20
    summer_start = 21
    autumn_start = 22
    winter_start = 21

    if month == 3 and day >= spring_start or month == 4 or month == 5 or (month == 6 and day < summer_start):
        return 'Spring'
    elif month == 6 and day >= summer_start or month == 7 or month == 8 or (month == 9 and day < autumn_start):
        return 'Summer'
    elif month == 9 and day >= autumn_start or month == 10 or month == 11 or (month == 12 and day < winter_start):
        return 'Autumn'
    else:
        return 'Winter'


# this is a template modal that makes the info help text work
# edit at your own risk!
def build_modal_info_overlay(id, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div(
        [  # modal div
            html.Div(
                [  # content div
                    html.Div(
                        [
                            html.H4(
                                [
                                    "About this plot",
                                    html.Img(
                                        id=f"close-{id}-modal",
                                        src="assets/times-circle-solid.svg",
                                        n_clicks=0,
                                        className="info-icon",
                                        style={"margin": 0},
                                    ),
                                ],
                                className="container_title",
                                style={"color": "white"},
                            ),
                            dcc.Markdown(content),
                        ]
                    )
                ],
                className=f"modal-content {side}",
            ),
            html.Div(className="modal"),
        ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div


# import all data for figures below
# this is from the starting dataset
localdf = pd.read_csv("assets/peakdatemodified_wl_local_event_stats.csv")
lookup = pd.read_csv("assets/station_data.csv")

# Define the order of seasons
season_order = ['Spring', 'Summer', 'Autumn', 'Winter']

# Trim date
localdf['trimmed_date'] = localdf['date_start'].str[0:5]

# Map trimmed date to season and create a new column
localdf['season'] = localdf['trimmed_date'].apply(get_season)

# Group by 'season' and count the number of rows in each group
season_counts = localdf['season'].value_counts().rename(localdf['station_name']).reindex(
    season_order)  # Use filename as column name

import plotly.graph_objects as go

# Sample data
monochromatics = [
    '#ff6347',  # Tomato
    '#dc143c',  # Crimson
    '#add8e6',  # Light blue
    '#87ceeb',  # Sky blue
    '#6495ed',  # Cornflower blue
    '#4169e1',  # Royal blue
    '#0000ff',  # Blue
    '#00008b',  # Dark blue
    '#90ee90',  # Light green
    '#7cfc00',  # Lawn green
    '#32cd32',  # Lime green
    '#228b22',  # Forest green
    '#008000',  # Green
    '#006400',  # Dark green
    '#d2b48c',  # Tan
    '#bc8f8f',  # Rosy brown
    '#8b4513',  # Saddle brown
    '#a0522d',  # Sienna
    '#8b0000'  # Dark red
]

locations = [
    "PointeClaire",
    "MontrealJetee1",
    "Varennes",
    "Contrecoeur-IOC",
    "Sorel",
    "LacSaintPierre",
    "Port-Saint-Francois",
    "TroisRivieres",
    "Becancour",
    "Batiscan",
    "Deschaillons-sur-Saint-Laurent",
    "Portneuf",
    "Neuville",
    "Vieux-Quebec",
    "Lauzon",
    "Saint-Laurent-IO",
    "Saint-Joseph-de-la-Rive",
    "Rimouski",
    "Sept-Iles"
]

labs = [
    'ptc',
    'mtr',
    'var',
    'con',
    'sor',
    'lsp',
    'psf',
    'trr',
    'bec',
    'bat',
    'des',
    'por',
    'neu',
    'vqc',
    'lau',
    'slio',
    'sjr',
    'rim',
    'sep'
]

# Create a mapping of location to color
location_colors = dict(zip(locations, monochromatics))

# Group by 'station_name' and 'season', and count the number of observations
season_counts = localdf.groupby(['station_name', 'season']).size().unstack(fill_value=0)

# Create a trace for each station
traces = []
for station in locations:
    trace = go.Bar(
        x=season_counts.columns,
        y=season_counts.loc[station],
        name=station,
        marker_color=location_colors[station]
    )
    traces.append(trace)

# Create layout
layout = go.Layout(
    title='Number of Extreme Events for Each Season by Station, 1970-2022',
    xaxis=dict(title='Season'),
    yaxis=dict(title='Number of Observations'),
    barmode='group'  # Use 'group' for grouped bar plot
)

# Create figure
histoFig = go.Figure(data=traces, layout=layout)

localdf['days'] = localdf['duration'] / 24

denseFig = go.Figure()
denseFig = px.density_heatmap(localdf, x="stn_lab", y="max", nbinsx=40, nbinsy=40, color_continuous_scale='aggrnyl',
                              category_orders={'stn_lab': labs})
denseFig.update_layout(title="Saturation of Peakness by Station, 1970-2022", xaxis_title="Station Label",
                       yaxis_title="Peak Water Level")

# Define mapping of labels to groups
label_to_group = {
    'ptc': 1, 'mtr': 1,
    'var': 2, 'con': 2, 'sor': 2, 'lsp': 2, 'psf': 2, 'trr': 2,
    'bec': 3, 'bat': 3, 'des': 3, 'por': 3, 'neu': 3, 'vqc': 3,
    'lau': 4, 'slio': 4, 'sjr': 4, 'rim': 4, 'sep': 4
}


# Define a function to map labels to groups
def map_label_to_group(label):
    return label_to_group[label]


# Apply the function to create the 'domain' column
localdf['domain'] = localdf['stn_lab'].apply(lambda x: map_label_to_group(x))

pieFig = go.Figure()
pieFig = px.treemap(localdf, path=['domain', 'station_name', 'ind_in_stn'],
                    color='max', color_continuous_scale='aggrnyl', hover_data=['date_max', 'days', 'mean'],
                    color_continuous_midpoint=np.average(localdf['max'], weights=localdf['days']))
pieFig.update_layout(title="Max Events per Station by Peakness")

# localdf['max_std']= [localdf['max']- localdf['max'].mean() ]/ localdf['max'].std(ddof=0)
# localdf['min_std']= [localdf['min']- localdf['min'].mean() ]/ localdf['min'].std(ddof=0)
# localdf['mean_std']= [localdf['mean']- localdf['mean'].mean() ]/ localdf['mean'].std(ddof=0)

# Calculate standardization for 'max' column
localdf['max_std'] = localdf['max'].apply(lambda x: (x - localdf['max'].mean()) / localdf['max'].std(ddof=0))

# Calculate standardization for 'min' column
localdf['days_std'] = localdf['days'].apply(lambda x: (x - localdf['days'].mean()) / localdf['days'].std(ddof=0))

# Calculate standardization for 'mean' column
localdf['mean_std'] = localdf['mean'].apply(lambda x: (x - localdf['mean'].mean()) / localdf['mean'].std(ddof=0))

# Create a dictionary to map each location to its rank
location_rank = {location: rank + 1 for rank, location in enumerate(locations)}

# Apply the rank to the 'station_name' column
localdf['rank'] = localdf['station_name'].map(lambda x: location_rank.get(x, None))

# Sort the DataFrame by the 'rank' column
localdf = localdf.sort_values("rank")

scatterFig = px.scatter_ternary(localdf, a="max_std", b="mean_std", c="days_std", color="station_name",
                                size="peak_ind", size_max=10,
                                color_discrete_sequence=monochromatics)

df = pd.read_csv('assets/station_data.csv')
mainFig = go.Figure()

# Create a trace for each station
traces = []
for station in locations:
    tempdf = df.loc[(df['station_name'] == station)]
    temp1df = localdf.loc[(localdf['station_name'] == station)]
    for x in range(temp1df.shape[0]):
        if x == 0:
            trace = mainFig.add_trace(go.Scattergeo(
                lon=tempdf['lon'],
                lat=tempdf['lat'],
                text=[temp1df['stn_lab'].iloc[x], temp1df['duration'].iloc[x],
                      temp1df['max'].iloc[x], temp1df['mean'].iloc[x], temp1df['min'].iloc[x]],
                marker=dict(
                    size=temp1df['max'].iloc[x],
                    color=location_colors[station],
                    line_color='rgb(40,40,40)',
                    line_width=0.5,
                    sizemode='area'),
                legendgroup='station_name',
                name=station))
        else:
            trace = mainFig.add_trace(go.Scattergeo(
                lon=tempdf['lon'],
                lat=tempdf['lat'],
                text=[temp1df['stn_lab'].iloc[x], temp1df['duration'].iloc[x],
                      temp1df['max'].iloc[x], temp1df['mean'].iloc[x], temp1df['min'].iloc[x]],
                marker=dict(
                    size=temp1df['max'].iloc[x],
                    color=location_colors[station],
                    line_color='rgb(40,40,40)',
                    line_width=0.5,
                    sizemode='area'),
                legendgroup='station_name',
                showlegend=False,
                name=station))
        traces.append(trace)

mainFig.update_layout(
    title_text='MAX',
    showlegend=True,
    geo=dict(
        landcolor='rgb(217, 217, 217)',
        projection_scale=30,
        center=dict(lat=df['lat'].iloc[2], lon=df['lon'].iloc[2]),  # this will center on the point
    )
)

musicdf = pd.read_csv("assets/mxmh_survey_results.csv")
# this is from the datasets that'll be added later
whddf = pd.read_csv("assets/WHD.csv")
whd15df = whddf.set_index('Country').query("Year==2015")
whd15df = whd15df.drop(columns=['Year'])
whd15df["Happiness Ratio"] = 1 / whd15df["Happiness Rank"]
whd19df = whddf.set_index('Country').query("Year==2019")
whd19df = whd19df.drop(columns=['Year'])
whd19df["Happiness Ratio"] = 1 / whd19df["Happiness Rank"]

# add all constants and code associated with data churning below
musicdf = musicdf.drop(columns=['Timestamp', 'Permissions'])
# you can decide how to handle missing data per column
# for example, with age you might want to impute a value based on the mean
musicdf["Age"] = musicdf["Age"].fillna(value=round(musicdf.Age.mean()))
# for something like music effects, you might want to assume no effect since it was not reported
musicdf["Music effects"] = musicdf["Music effects"].fillna(value="No effect")
musicdf["While working"] = musicdf["While working"].fillna(value="No")
musicdf["Instrumentalist"] = musicdf["Instrumentalist"].fillna(value="No")
musicdf["Composer"] = musicdf["Composer"].fillna(value="No")
musicdf["Primary streaming service"] = musicdf["Primary streaming service"].fillna(
    value="I do not use a streaming service.")
# feel free to impute missing values however you wish for your data
# you can also make new values
musicdf["Mental health severity"] = musicdf["Anxiety"] + musicdf["Depression"] + musicdf["Insomnia"] + musicdf["OCD"]
# data churning is done!!!
#
# # time to create figures

# this is what makes the web server look pretty
app.layout = html.Div(
    children=[
        html.Div(
            [  # title section with your logo can go here
                html.H1(
                    children=[
                        "Water Levels around the St. Lawrence",
                        html.A(
                            html.Img(
                                src="assets/canada.png",
                                style={"float": "right", "height": "75px"},
                            ),
                            href="https://www.canada.ca/en/environment-climate-change.html",
                        ),
                    ],
                    style={"text-align": "left", "color": "#ffffff"},
                ),
            ]
        ),
        html.Div(
            children=[  # this contains the intro text and the toggle buttons
                html.H4("Application overview", style={"margin-top": "0"}),
                dcc.Markdown(
                    """
            Under the governmental Flood Hazard Identification and Mapping Program (FHIMP), 
            Environment and Climate Change Canada (ECCC) has been mandated to provide 2D simulations 
            of extreme water levels in the St. Lawrence fluvial estuary under historical 
            and future conditions. The elevations of water levels in this system are triggered 
            by the complex interaction of hydrological, meteorological, and tidal processes 
            that must be considered to simulate river dynamics and flood events. 

            Constraints on the computational resources and time requirements and the necessity 
            for background geophysical fields currently limit the feasibility of producing 
            fine-scale 2D hydrodynamic simulations to a limited set of relatively short 
            extreme events. The project domain goes from Montreal to Saint-Joseph-de-la-Rive. 
            This spans 450 km and includes two fluvial lakes (Lac Saint Luis and Lac Saint-Pierre). 
            The domain can be schematically divided in four sections:

            1. Montreal region where the Ontario Lake outflow and Ottawa River streamflow controls the water levels fluctuations.
            2. Varennes to Trois-Rivières where water levels are mainly influenced by long-term hydrological trends and the annual hydrological cycles. This region includes Lac Saint-Pierre (fluvial lake), as well as some important tributaries (Richelieu, Yamaska, Saint-François and Saint-Maurice rivers).
            3. Trois-Rivières to Québec where water level variability is mainly driven by semi-diurnal and diurnal tides, as well as by the daily to seasonal variability of the river streamflow. Several tributaries are also present, mostly on the North shore.
            4. Île-d'Orléans to Saint-Joseph-de-la-Rive where water transition from brackish to salty. Tide and storm waves are the main contributor to the water level variability.


            Click the buttons to load sample data sets and explore the interactivity of the plots.
            """
                ),
                html.Div(
                    children=[
                        html.Button(
                            "Canada",
                            id="can",
                            className="button",
                            style={"padding-left": "10px", "padding-right": "10px",
                                   "margin-left": "10px", "margin-right": "10px"}
                        ),
                        html.Button(
                            "DEMO - Music And Mental Health",
                            id="mxmh",
                            className="button",
                            style={"padding-left": "10px", "padding-right": "10px",
                                   "margin-left": "10px", "margin-right": "10px"}
                        ),
                        html.Button(
                            "DEMO - World Happiness Data 2019",
                            id="whd19",
                            className="button",
                            style={"padding-left": "10px", "padding-right": "10px",
                                   "margin-left": "10px", "margin-right": "10px"}
                        ),
                        html.Button(
                            "DEMO - World Happiness Data 15-19",
                            id="whd",
                            className="button",
                            style={"padding-left": "10px", "padding-right": "10px",
                                   "margin-left": "10px", "margin-right": "10px"}
                        )
                    ],
                ),
            ],
            style={
                "width": "98%",
                "margin-right": "0",
                "padding": "10px",
            },
            className="twelve columns pretty_container",
        ),
        html.Div(
            children=[  # this does the help text for each of the help modals
                build_modal_info_overlay(
                    "histo",
                    "bottom",
                    dedent(
                        """
            The _**Histogram example**_ panel displays an example of the Histogram plot. You can edit this panel to
            contain information that is relevant to the plot you created. 

            [You can learn more about Histograms at this link](https://plotly.com/python/histograms/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "dense",
                    "bottom",
                    dedent(
                        """
            The _**Density map example **_ panel displays an example of the Density map plot. You can edit this panel to
            contain information that is relevant to the plot you created. 

            [You can learn more about Density Map plots at this link](https://plotly.com/python/2D-Histogram/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "main",
                    "bottom",
                    dedent(
                        """
            The _**Main plot example **_ panel displays an example of a larger plot within the scheme of the app. 
            You can edit this panel to contain information that is relevant to the plot you created. 

            [Plotly has all sorts of examples for plots, you can see all of them here.](https://plotly.com/python/plotly-express/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "pie",
                    "top",
                    dedent(
                        """
            The _**Pie example **_ panel displays an example of a Pie plot. You can edit this panel to
            contain information that is relevant to the plot you created. 

            [You can learn more about Pie plots at this link](https://plotly.com/python/sunburst-charts/).
        """
                    ),
                ),
                build_modal_info_overlay(
                    "scatter",
                    "top",
                    dedent(
                        """
            The _**Scatter example **_ panel displays an example of a Scatter plot. You can edit this panel to
            contain information that is relevant to the plot you created. 

            [You can learn more about Scatter plots at this link](https://plotly.com/python/line-and-scatter/).
        """
                    ),
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[  # contains the top row charts
                                html.H4(
                                    [
                                        "Extreme Events by Season",  # top left chart
                                        html.Img(
                                            id="show-histo-modal",
                                            src="assets/question-circle-solid.svg",
                                            n_clicks=0,
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="histo-graph",
                                        figure=histoFig,
                                        config={"displayModeBar": False},
                                    ),
                                    className="svg-container",
                                    style={"height": 150},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="histo-div",
                        ),
                        html.Div(
                            children=[
                                html.H4(
                                    [
                                        "Concentration of Peak Extreme Events",  # top right chart
                                        html.Img(
                                            id="show-dense-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="dense-graph",
                                    figure=denseFig,
                                    config={"displayModeBar": False},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="dense-div",
                        ),
                    ]
                ),
                html.Div(
                    children=[  # this contains the main chart
                        html.H4(
                            [
                                "Main Plot Example - Time Series Map Evolution of Extreme Events",
                                html.Img(
                                    id="show-main-modal",
                                    src="assets/question-circle-solid.svg",
                                    className="info-icon",
                                ),
                            ],
                            className="container_title",
                        ),
                        dcc.Graph(
                            id="main-graph",
                            figure=mainFig,
                        ),
                    ],
                    className="twelve columns pretty_container",
                    style={
                        "width": "98%",
                        "margin-right": "0",
                    },
                    id="main-div",
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[  # this contains the bottom row charts
                                html.H4(
                                    [
                                        "Tree Plot - All Extreme Events",  # left plot
                                        html.Img(
                                            id="show-pie-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="pie-graph",
                                    figure=pieFig,
                                    config={"displayModeBar": False},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="pie-div",
                        ),
                        html.Div(
                            children=[
                                html.H4(
                                    [
                                        "Standardized Max/Mean/Duration of Event By Station",  # right plot
                                        html.Img(
                                            id="show-scatter-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="scatter-graph",
                                    config={"displayModeBar": False},
                                    figure=scatterFig,
                                ),
                            ],
                            className="six columns pretty_container",
                            id="scatter-div",
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            children=[  # the acknowledgments section

                html.H4("Acknowledgements", style={"margin-top": "0"}),
                dcc.Markdown(
                    """\

                This app was developed for the 14th 
                [Fourteenth Montreal Industrial Problem Solving Workshop](https://www.crmath.ca/en/activities/#/type/activity/id/3955),
                hosted by the Centre de recherches mathématiques (CRM), the Institute for Data Valorization (IVADO), and GERAD. 
                 - Dashboard written in Python using the [Plotly](https://plotly.com) [Dash](https://dash.plot.ly/) web framework.
                 - The front-end is based off of [World Cell Towers](https://dash.gallery/dash-world-cell-towers/) found 
                 [here](https://dash.gallery/Portal/) and a blank repo for general use can be found [here](https://github.com/kristen-hallas/UTRGV-FronteraHacks23-Dash).
                 - For huge data, parallel and distributed calculations can be implemented using the [Dask](https://dask.org/) 
                 Python library.
                 - Icons provided by [Font Awesome](https://fontawesome.com/) and used under the
                [_Font Awesome Free License_](https://fontawesome.com/license/free). 
                 - Primary dataset is from Environment and Climate Change Canada (ECCC), courtesy of Silvia Innocenti,
                 [GitHub](https://github.com/SlvInn). ECCC provided data suitable for a benchmark analysis, including the following datasets for the 1970-2022 period: hourly water level records observed at 15 stations over the study domain; hourly water level reconstructions at 2 stations obtained with a non-stationary tidal harmonic regression tool and the corresponding regressors; 2D hydrodynamics simulations corresponding to a subset of extreme events observed at the selected stations.
                 - Demo datasets are from Catherine Rasgaitis on Kaggle, [Music & Mental Health Survey Results](https://www.kaggle.com/datasets/catherinerasgaitis/mxmh-survey-results). World Happiness Report data was collated/cleaned by Kristen Hallas, sourced from the 
                 [World Happiness Report](https://www.kaggle.com/datasets/unsdsn/world-happiness) on Kaggle. 

                ### Remarks
                * this layout is compatible with Markdown
                * includes baked-in help modals (click the ? icon!)
                * callback function buttons that swap out datasets (and can do so much more - 
                [definitely worth the research](https://dash.plotly.com/basic-callbacks)) 
                * parallelizable for large datasets, such as time series

                """
                ),
            ],
            style={
                "width": "98%",
                "margin-right": "0",
                "padding": "10px",
            },
            className="twelve columns pretty_container",
        ),
    ],
)

# callbacks
# this is what makes the app interactive

# first function create show/hide callbacks for each info modal
# if you change any of the IDs above, you need to change them here
# change at your own risk
for id in ["histo", "dense", "main", "pie", "scatter"]:

    @app.callback(
        [Output(f"{id}-modal", "style"), Output(f"{id}-div", "style")],
        [Input(f"show-{id}-modal", "n_clicks"), Input(f"close-{id}-modal", "n_clicks")],
    )
    def toggle_modal(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("show-"):
            return {"display": "block"}, {"zIndex": 1003}
        else:
            return {"display": "none"}, {"zIndex": 0}


# create callback to show each graph. you can't do multiple callbacks that use the same output/input ID
# so that's why we do it in a big function like this
# if you need help understanding each of the graph plots I comment about them up at their initialization
@app.callback([
    Output("histo-graph", "figure"),
    Output("dense-graph", "figure"),
    Output("main-graph", "figure"),
    Output("pie-graph", "figure"),
    Output("scatter-graph", "figure")],
    [Input("mxmh", "n_clicks"),
     Input("can", "n_clicks"),
     Input("whd19", "n_clicks"),
     Input("whd", "n_clicks")], prevent_initial_call=True)
# you need the number of input in update_graphs to match the number of buttons you have updating graphs
def update_graphs(b1, b2, b3, b4):
    triggered_id = ctx.triggered[0]['prop_id']
    if 'mxmh.n_clicks' == triggered_id:
        return update_mxmh()
    elif 'can.n_clicks' == triggered_id:
        return update_can()
    elif 'whd19.n_clicks' == triggered_id:
        return update_whd19()
    else:
        return update_whd()


# the output should be returning the figures you wanted to update
def update_mxmh():
    mainFig = go.Figure()
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Depression'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Depression/10', scalegroup='Depression/10', name='Depression/10',
                                line_color='hotpink', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Anxiety'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Anxiety/10', scalegroup='Anxiety/10', name='Anxiety/10',
                                line_color='green', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['OCD'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='OCD/10', scalegroup='OCD/10', name='OCD/10',
                                line_color='blue', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Insomnia'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Insomnia/10', scalegroup='Insomnia/10', name='Insomnia/10',
                                line_color='purple', box_visible=True)
                      )
    mainFig.update_traces(meanline_visible=True)
    mainFig.update_layout(violingap=0, violinmode='group')
    mainFig.update_layout(yaxis_title="Self-Ranked Score Out of 10",
                          xaxis_title="Music Tends to ______ My Mental Health")

    histoFig = px.histogram(musicdf, x="Fav genre", histfunc='count', color="Music effects",
                            color_discrete_sequence=px.colors.qualitative.Prism)
    histoFig.update_layout(yaxis_title="Number of People")

    denseFig = px.density_heatmap(musicdf, x="Depression", y="Anxiety", nbinsx=10, nbinsy=10, facet_row="Composer",
                                  facet_col="Instrumentalist")

    scatterFig = px.scatter_ternary(musicdf, a="OCD", b="Anxiety", c="Insomnia", color="Exploratory",
                                    size="Mental health severity", size_max=20,
                                    color_discrete_sequence=px.colors.qualitative.Prism)

    pieFig = px.sunburst(musicdf, path=['Primary streaming service', 'Exploratory'], values='Hours per day',
                         color='Primary streaming service', color_discrete_sequence=px.colors.sequential.Plasma)
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_can():
    # Create a trace for each station
    traces = []
    for station in locations:
        trace = go.Bar(
            x=season_counts.columns,
            y=season_counts.loc[station],
            name=station,
            marker_color=location_colors[station]
        )
        traces.append(trace)

    # Create layout
    layout = go.Layout(
        title='Number of Extreme Events for Each Season by Station, 1970-2022',
        xaxis=dict(title='Season'),
        yaxis=dict(title='Number of Observations'),
        barmode='group'  # Use 'group' for grouped bar plot
    )

    # Create figurea
    histoFig = go.Figure(data=traces, layout=layout)

    denseFig = px.density_heatmap(localdf, x="stn_lab", y="max", nbinsx=40, nbinsy=40, color_continuous_scale='aggrnyl',
                                  category_orders={'stn_lab': labs})
    denseFig.update_layout(title="Saturation of Peakness by Station, 1970-2022", xaxis_title="Station Label",
                           yaxis_title="Peak Water Level")

    pieFig = px.treemap(localdf, path=['domain', 'station_name', 'ind_in_stn'],
                        color='max', color_continuous_scale='aggrnyl', hover_data=['date_max', 'days', 'mean'],
                        color_continuous_midpoint=np.average(localdf['max'], weights=localdf['days']))
    pieFig.update_layout(title="Max Events per Station by Peakness")

    scatterFig = px.scatter_ternary(localdf, a="max_std", b="mean_std", c="days_std", color="station_name",
                                    size="peak_ind", size_max=10,
                                    color_discrete_sequence=monochromatics)
    # Create a trace for each station
    traces = []
    for station in locations:
        tempdf = df.loc[(df['station_name'] == station)]
        temp1df = localdf.loc[(localdf['station_name'] == station)]
        for x in range(temp1df.shape[0]):
            if x == 0:
                trace = mainFig.add_trace(go.Scattergeo(
                    lon=tempdf['lon'],
                    lat=tempdf['lat'],
                    text=[temp1df['stn_lab'].iloc[x], temp1df['duration'].iloc[x],
                          temp1df['max'].iloc[x], temp1df['mean'].iloc[x], temp1df['min'].iloc[x]],
                    marker=dict(
                        size=temp1df['max'].iloc[x],
                        color=location_colors[station],
                        line_color='rgb(40,40,40)',
                        line_width=0.5,
                        sizemode='area'),
                    legendgroup='station_name',
                    name=station))
            else:
                trace = mainFig.add_trace(go.Scattergeo(
                    lon=tempdf['lon'],
                    lat=tempdf['lat'],
                    text=[temp1df['stn_lab'].iloc[x], temp1df['duration'].iloc[x],
                          temp1df['max'].iloc[x], temp1df['mean'].iloc[x], temp1df['min'].iloc[x]],
                    marker=dict(
                        size=temp1df['max'].iloc[x],
                        color=location_colors[station],
                        line_color='rgb(40,40,40)',
                        line_width=0.5,
                        sizemode='area'),
                    legendgroup='station_name',
                    showlegend=False,
                    name=station))
            traces.append(trace)

    mainFig.update_layout(
        title_text='MAX',
        showlegend=True,
        geo=dict(
            landcolor='rgb(217, 217, 217)',
            projection_scale=30,
            center=dict(lat=df['lat'].iloc[2], lon=df['lon'].iloc[2]),  # this will center on the point
        )
    )
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_whd19():
    mainFig = px.choropleth(whd19df, locations="iso_alpha",
                            color="Happiness Score", fitbounds='locations',
                            hover_name=whd19df.index, hover_data=['Economy (GDP per Capita)', 'Family',
                                                                  'Health (Life Expectancy)', 'Freedom',
                                                                  'Trust (Government Corruption)', 'Generosity'],
                            color_continuous_scale=px.colors.sequential.RdBu)
    mainFig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation='h', y=-0.1, yanchor='bottom', x=0.5, xanchor='center'))

    histoFig = px.histogram(whd19df, x="Happiness Score", y='Health (Life Expectancy)', histfunc='avg',
                            color="Region", color_discrete_sequence=px.colors.sequential.Plasma)

    tempdf = whd19df.where(whd19df["Happiness Score"] > 5)
    scatterFig = px.scatter_3d(tempdf,
                               x="Economy (GDP per Capita)", y="Trust (Government Corruption)", z="Freedom",
                               color='Region', hover_name=whd19df.index,
                               hover_data=['Economy (GDP per Capita)', 'Family',
                                           'Health (Life Expectancy)', 'Freedom',
                                           'Trust (Government Corruption)',
                                           'Generosity'],
                               color_discrete_sequence=px.colors.sequential.Plasma)

    denseFig = px.treemap(whd19df, path=[px.Constant("world"), 'Region', whd19df.index], values='Happiness Ratio',
                          color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                          color_continuous_midpoint=np.average(whd19df['Happiness Score'],
                                                               weights=whd19df['Happiness Ratio'])
                          )
    denseFig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    pieFig = px.sunburst(whd19df, path=['Region', whd19df.index], values='Happiness Ratio',
                         color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                         color_continuous_midpoint=np.average(whd19df['Happiness Score'],
                                                              weights=whd19df['Happiness Ratio']))
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_whd():
    mainFig = px.choropleth(whddf, locations="iso_alpha",
                            color="Happiness Score", fitbounds='locations',
                            hover_name="Country", hover_data=['Economy (GDP per Capita)', 'Family',
                                                              'Health (Life Expectancy)', 'Freedom',
                                                              'Trust (Government Corruption)', 'Generosity'],
                            color_continuous_scale=px.colors.sequential.RdBu, animation_frame="Year")
    mainFig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation='h', y=-0.1, yanchor='bottom', x=0.5, xanchor='center'))

    histoFig = px.histogram(whddf, x="Happiness Score", histfunc='count', color="Region",
                            color_discrete_sequence=px.colors.sequential.Plasma,
                            animation_frame="Year")
    histoFig.update_layout(yaxis_title="Number of Countries")

    scatterFig = px.scatter_ternary(whddf, a="Generosity", b="Trust (Government Corruption)", c="Freedom",
                                    hover_name="Country", color="Region", size="Happiness Score", size_max=15,
                                    hover_data=['Happiness Score', 'Economy (GDP per Capita)', 'Family',
                                                'Health (Life Expectancy)', 'Freedom',
                                                'Trust (Government Corruption)', 'Generosity'],
                                    animation_frame="Year", color_discrete_sequence=px.colors.sequential.Plasma)

    denseFig = px.treemap(whddf, path=[px.Constant("world"), 'Region', 'Country'], values='Economy (GDP per Capita)',
                          color='Happiness Score', hover_data=['Economy (GDP per Capita)'],
                          color_continuous_scale='RdBu',
                          color_continuous_midpoint=np.average(whddf['Happiness Score'],
                                                               weights=whddf['Economy (GDP per Capita)']))
    denseFig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    pieFig = px.sunburst(whddf, path=['Region', 'Country'], values='Trust (Government Corruption)',
                         color='Happiness Score', hover_data=['iso_alpha'],
                         color_continuous_scale='RdBu',
                         color_continuous_midpoint=np.average(whddf['Happiness Score'],
                                                              weights=whddf['Trust (Government Corruption)']))

    return histoFig, denseFig, mainFig, pieFig, scatterFig


# FYI you can't have multiple callbacks with the same id so don't try lol

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
