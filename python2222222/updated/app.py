from flask import Flask, request, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Load datasets
air_quality_data = pd.read_csv('AirQuality.csv')
crime_data = pd.read_csv('crime.csv')
ict_data = pd.read_csv('ICT_Subdimension_Dataset.csv')

# Clean and preprocess data
air_quality_data.ffill(inplace=True)
crime_data.ffill(inplace=True)
ict_data.ffill(inplace=True)

# Initialize Flask app
app = Flask(__name__)

# Function for basic analysis
def basic_analysis(df):
    return df.describe().to_html()

# Function for creating charts with Plotly
def generate_charts(df, dataset_name):
    charts = {}

    if dataset_name == "air_quality":
        # Line Chart for pollutant trends over time
        fig = px.line(df, x='Date', y=['PM2.5', 'PM10', 'CO', 'O3'], title="Air Quality Trends")
        charts['line_chart'] = pio.to_html(fig, full_html=False)
        
        # Scatter Plot for pollutant relationships
        fig = px.scatter(df, x='PM2.5', y='AQI', color='City', title="Scatter Plot of PM2.5 vs AQI")
        charts['scatter_plot'] = pio.to_html(fig, full_html=False)
        
        # Heatmap of correlations
        fig = px.imshow(df[['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']].corr(), 
                        text_auto=True, title="Air Quality Correlation Heatmap")
        charts['heatmap'] = pio.to_html(fig, full_html=False)
    
    elif dataset_name == "crime":
        # Bar Chart for crime frequency by type
        fig = px.bar(df, x='Crime Description', title="Crime Frequency by Type")
        charts['bar_chart'] = pio.to_html(fig, full_html=False)

        # Time Series for crime occurrences over time
        df['Date of Occurrence'] = pd.to_datetime(df['Date of Occurrence'])
        fig = px.histogram(df, x='Date of Occurrence', title="Crime Occurrences Over Time")
        charts['time_series'] = pio.to_html(fig, full_html=False)
        
        # Heatmap of crime types by age
        fig = px.density_heatmap(df, x="Victim Age", y="Crime Code", title="Crime Types by Victim Age")
        charts['heatmap'] = pio.to_html(fig, full_html=False)
    
    elif dataset_name == "ict":
        # Radar Chart for ICT subdimensions
        fig = px.line_polar(df, r="Household Internet Access (%)", theta="City", 
                            line_close=True, title="ICT Subdimension Radar Chart")
        charts['radar_chart'] = pio.to_html(fig, full_html=False)

        # Bar Chart for smart device adoption by city
        fig = px.bar(df, x='City', y=['Smart Water Meters (%)', 'Smart Electricity Meters (%)'], 
                     title="Smart Device Adoption by City", barmode="group")
        charts['bar_chart'] = pio.to_html(fig, full_html=False)
        
        # Heatmap for ICT coverage correlation
        fig = px.imshow(df[['Household Internet Access (%)', 'Wireless Broadband Coverage 3G (%)', 
                            'Wireless Broadband Coverage 4G (%)', 'Smart Water Meters (%)', 
                            'Intersection Control (%)']].corr(), text_auto=True, 
                        title="ICT Coverage Correlation Heatmap")
        charts['heatmap'] = pio.to_html(fig, full_html=False)

    return charts

# Route for homepage with search functionality
@app.route('/', methods=['GET', 'POST'])
def index():
    search_city = ''
    results = None
    summary_stats = {}
    charts = {}

    if request.method == 'POST':
        search_city = request.form['city_name'].strip().title()

        # Search in air quality data
        air_quality_results = air_quality_data[air_quality_data['City'] == search_city]

        # Search in crime data
        crime_results = crime_data[crime_data['City'] == search_city]

        # Search in ICT data
        ict_results = ict_data[ict_data['City'] == search_city]

        results = {
            'air_quality': air_quality_results.to_dict(orient='records'),
            'crime': crime_results.to_dict(orient='records'),
            'ict': ict_results.to_dict(orient='records'),
        }

        # Basic analysis and visualizations
        datasets = {
            'air_quality': air_quality_results,
            'crime': crime_results,
            'ict': ict_results,
        }

        for key, dataset in datasets.items():
            if not dataset.empty:
                summary_stats[key] = basic_analysis(dataset)
                charts[key] = generate_charts(dataset, key)

    return render_template('index.html', city=search_city, results=results,
                           summary_stats=summary_stats, charts=charts)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
