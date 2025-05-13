import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import zipfile
import os

# Suppress warnings
import warnings

# Suppress the specific deprecation warning for use_column_width
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Page config
st.set_page_config(layout="wide")

# Title and banner
st.markdown("<h1 style='text-align: center;'>EXPLORING MENTAL HEALTH HELP-SEEKING JOURNEY</h1>", unsafe_allow_html=True)
st.image("banner2.png", use_column_width=False, width = 1200) 

# Load data
import zipfile
import os

# Path to the uploaded zip file
zip_file_path = "Final_Data.csv.zip"
extract_folder = "data"

# Ensure the directory exists
if not os.path.exists(extract_folder):
    os.makedirs(extract_folder)

# Unzip the file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

# Load the CSV from the extracted folder
df = pd.read_csv(os.path.join(extract_folder, "Final_Data.csv"))

# Extract Year from Timestamp
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df = df.dropna(subset=['Timestamp'])
df['Year'] = df['Timestamp'].dt.year

# Sidebar Filters
# Initialize filtered as a copy of df
filtered = df.copy()

# Sidebar Filters
st.sidebar.header("Filter Data")
genders = df['Gender'].dropna().unique()
occupations = df['Occupation'].dropna().unique()
countries = df['Country'].dropna().unique()
years = sorted(df['Year'].unique())

gender_sel = st.sidebar.multiselect("Gender", options=genders, default=[])
occ_sel    = st.sidebar.multiselect("Occupation", options=occupations, default=[])
ctry_sel   = st.sidebar.multiselect("Country", options=countries, default=[])
year_sel   = st.sidebar.multiselect("Year", options=years, default=[])

if gender_sel:
    filtered = filtered[filtered['Gender'].isin(gender_sel)]
if occ_sel:
    filtered = filtered[filtered['Occupation'].isin(occ_sel)]
if ctry_sel:
    filtered = filtered[filtered['Country'].isin(ctry_sel)]
if year_sel:
    filtered = filtered[filtered['Year'].isin(year_sel)]


# Displaying overall Metrics
col1, col2, col3 = st.columns(3)
totals = filtered.shape[0]
avg_str = filtered['Stress_Score_Balanced'].mean()
country_count = filtered['Country'].nunique()

col1.markdown(f"<h3>Total Respondents</h3><h2 style='color: #A3C6F1;'>{totals:,}</h2>", unsafe_allow_html=True)
col2.markdown(f"<h3>No. of Countries</h3><h2 style='color: #A8D8A3;'>{country_count:,}</h2>", unsafe_allow_html=True)
col3.markdown(f"<h3>Avg Stress Score</h3><h2 style='color: #F28D8D;'>{avg_str:.2f}</h2>", unsafe_allow_html=True)

st.markdown("---")

# Common settings for plots
COMMON = dict(
    template='plotly_white', title_x=0.5,
    font=dict(family='Arial', size=12),
    margin=dict(l=40, r=40, t=50, b=40)
)

# Visualization 1: Treatment Rate by Country (Bar Chart)
ctr = filtered.groupby('Country')['Treatment_Encoded'].mean().reset_index(name='rate')
ctr['rate_pct'] = (ctr['rate'] * 100).round(2)
fig1 = px.bar(
    ctr.sort_values('rate_pct', ascending=False),
    x='Country', y='rate_pct',
    title='Treatment Rate by Country',
    labels={'rate_pct':'Treatment Rate (%)'},
    hover_data={'rate_pct':':.2f'},
    color='rate_pct', color_continuous_scale='Plasma'
)
fig1.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)
st.plotly_chart(fig1, use_container_width=True)

# Visualization 2: Treatment Rate by Family History (Donut Chart)
fh = filtered.groupby('Family_history')['Treatment_Encoded'].mean().reset_index(name='rate')
fh['rate_pct'] = (fh['rate'] * 100).round(2)
fig2 = px.pie(
    fh, names='Family_history', values='rate_pct',
    title='Treatment Rate by Family History', hole=0.4,
    labels={'Family_history':'Family History','rate_pct':'Rate (%)'}
)
fig2.update_traces(textinfo='percent+label')
fig2.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)
st.plotly_chart(fig2, use_container_width=True)

# Visualization 3: Occupation & Self-employment by Treatment (Stacked Bar)
stack_data = filtered.groupby(['Occupation','Self_employed','Treatment_Encoded']).size().reset_index(name='count')
fig3 = px.bar(
    stack_data, x='Occupation', y='count', color='Self_employed',
    facet_col='Treatment_Encoded', barmode='stack',
    title='Occupation & Self-employment by Treatment',
    labels={'count':'Count','Self_employed':'Self-employed','Treatment_Encoded':'Treatment'}
)
fig3.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)
fig3.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
st.plotly_chart(fig3, use_container_width=True)

# Visualization 4: Barriers to Care (Pie Chart)
br = filtered['Care_options'].value_counts().reset_index(name='count')
br.columns = ['Barrier','count']
fig4 = px.pie(
    br, names='Barrier', values='count',
    title='Barriers to Care', hole=0.3
)
fig4.update_traces(textinfo='value+label')
fig4.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)
st.plotly_chart(fig4, use_column_width=True)

# Visualization 5: Average Stress Score by Country (Choropleth)
sa = filtered.groupby('Country')['Stress_Score_Balanced'].mean().reset_index(name='avg')
sa['avg'] = sa['avg'].round(2)
fig5 = px.treemap(
    sa, path=['Country'], values='avg', color='avg',
    color_continuous_scale='YlGnBu',
    hover_data={'avg':':.2f'},
    title='Average Stress Score by Country',
    labels={'avg': 'Avg Stress Score'}
)
fig5.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)
fig5.update_traces(hovertemplate="<b>%{label}</b><br>Avg Stress Score: %{value:.2f}<br><extra></extra>")
st.plotly_chart(fig5, use_container_width=True)

# Visualization 6: Average Stress Score by Days Indoors (Bar Chart)
df_plot = filtered.groupby('Days_indoors').agg(Avg_Stress=('Stress_Score_Balanced','mean'), Count=('Stress_Score_Balanced','size')).reset_index()
categories = ['Go out Every day','1-14 days','15-30 days','31-60 days','More than 2 months']
df_plot['Days_indoors'] = pd.Categorical(df_plot['Days_indoors'], categories=categories, ordered=True)
df_plot = df_plot.sort_values('Days_indoors')
fig6 = px.bar(
    df_plot, x='Days_indoors', y='Avg_Stress',
    title='Average Stress Score by Days Indoors',
    hover_data={'Count': True, 'Avg_Stress': ':.2f'},
    labels={'Days_indoors': 'Days Indoors', 'Avg_Stress': 'Average Stress Score'},
    color='Avg_Stress', color_continuous_scale='YlGnBu'
)
fig6.update_layout(
    title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 24, 'family': 'Arial'}},
    xaxis_title=None,
    yaxis_title='Average Stress Score',
    xaxis=dict(
        tickmode='array',
        tickvals=df_plot['Days_indoors'],
        ticktext=categories,
        tickangle=-45
    ),
    yaxis=dict(tickformat='.2f'),
    margin=dict(l=0, r=0, t=50, b=70),  
    font=dict(size=12, family='Arial', color='white'),  
    coloraxis_showscale=True,  
)

st.plotly_chart(fig6, use_container_width=True)

# Visualization 7: Average Stress by Isolation Level (Binned)
filtered['IsoBin'] = pd.cut(filtered['Isolation_Level_Balanced'], bins=np.linspace(0,1,11), include_lowest=True)

# Convert the Interval objects to strings
filtered['IsoBin_label'] = filtered['IsoBin'].astype(str)

# Create the average stress by isolation level
bin_avg = filtered.groupby(['IsoBin_label', 'Treatment_Encoded']).agg(Avg_Stress=('Stress_Score_Balanced', 'mean')).reset_index()

# Ensure the 'IsoBin_label' is treated as a categorical variable with an ordered category
bin_order = sorted(bin_avg['IsoBin_label'].unique())
bin_avg['IsoBin_label'] = pd.Categorical(bin_avg['IsoBin_label'], categories=bin_order, ordered=True)

# Plot the line chart
fig7 = px.line(
    bin_avg, x='IsoBin_label', y='Avg_Stress', color='Treatment_Encoded', markers=True,
    title='Average Stress by Isolation Level',
    labels={'IsoBin_label': 'Isolation Level Bin', 'Avg_Stress': 'Average Stress Score', 'Treatment_Encoded': 'Treatment'}
)

fig7.update_layout(title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 28}}, **COMMON)

# Display the plot
st.plotly_chart(fig7, use_container_width=True)


# Footer
st.markdown("---")
