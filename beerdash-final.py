# %%
import streamlit as st


st.set_page_config(layout='wide')


import numpy as np
import plotly.graph_objects as go
import seaborn as sns 
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import pandas as pd
import json
from streamlit_folium import st_folium
import re
from PIL import Image
from plotly.subplots import make_subplots

# !pip install folium
# !pip install geopandas
import geopandas as gpd
import folium

# zorgen dat mijn kolommen niet gelimiteerd zijn
pd.set_option('display.max_columns', None)

############################################### DATA INLADEN ##########################################

amerikaansbier = pd.read_csv("https://raw.githubusercontent.com/CoderendeAziaat/beerdash/288d64ce564acab5be52b48dc041e7016ecf5d03/amerikaansbier.csv")
eubier = pd.read_csv("https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/eubieren.csv")

#######################################################################################################

# ##################################################################
# 
# DATA CLEANEN. NIEUWE KOLOMMEN MAKEN 
# Nieuwe kolom 'state' uit 'region'
# De rating kolom opschonen. Strings er uit
# De ABV kolom opschonen
# De IBU kolom opschonen
# 
# ##################################################################

# Nieuwe kolom 'state' toevoegen die de staat haalt uit de kolom 'region'.

valid_states = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
}

# Filter de data om alleen rijen te behouden met een geldige staat
amerikaansbier = amerikaansbier[amerikaansbier["state"].isin(valid_states)]

# Nu zijn er nog maar 50 staten (en DC), dus 51 unique values in 'states', over.

# ##################################################################

# Verwijder rijen waar 'abv' NaN is (die konden niet worden geconverteerd)
amerikaansbier = amerikaansbier.dropna(subset=["abv"])

##################################################################
# 
# 3 KAARTEN MAKEN: WORDEN WEL GEBRUIKT IN DE APP
# HIERONDER WORDEN EERST DE JUISTE VARIABELEN GEMAAKT OM 
# DE KAARTEN TE KUNNEN MAKEN:
#
##################################################################
# %%
# Amerikaanse staten inladen:
url = "https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/us-states.json"

# Download en sla lokaal op
geojson_path = "us-states.json"
response = requests.get(url)

if response.status_code == 200:
    with open(geojson_path, "wb") as f:
        f.write(response.content)
    print("✅ GeoJSON succesvol gedownload!")

    # Lees het bestand in met geopandas
    statenkaart = gpd.read_file(geojson_path)
    print(statenkaart.head())  # Debug: Bekijk of de data correct is geladen
else:
    print("❌ Fout bij downloaden van GeoJSON:", response.status_code)

# statenkaart = gpd.read_file('us-states.json')
print(statenkaart.head())

# EU landen inladen:
eu_geojson_url = "https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/europe.geojson"

# Download en lokaal opslaan
eu_geojson_path = "europe.geojson"
response = requests.get(eu_geojson_url)

if response.status_code == 200:
    with open(eu_geojson_path, "wb") as f:
        f.write(response.content)
    print("✅ Europese GeoJSON succesvol gedownload!")
    
    # Lees het bestand in met geopandas
    europakaart = gpd.read_file(eu_geojson_path)
    print(europakaart.head())  # Debug: Bekijk of de data correct is geladen
else:
    print("❌ Fout bij downloaden van Europese GeoJSON:", response.status_code)

##################################################################
#
# DASHBOARD BOUWEN 
# 
##################################################################

# 3 TABBLADEN 
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Home of Beer", "VS vs. EU" ,"Beer Map", "Find Your Favorite Beer","Food Pairings", "Update-Log"])
with tab1:
    st.title("🍺 Welkom bij ons bierdashboard!")
    st.subheader("Lang geleden leefden alle naties in harmonie, verbonden door hun liefde voor bier. Van Europa tot Amerika, de bieren stroomden vrij. Maar toen viel Amerika de wereld aan met importheffingen, en de vrede brak uiteen. De wereld raakte verdeeld, en we moesten helaas onze bieren uit Europa zelf halen. Maar wees gerust, Europa heeft veel te bieden! De rijke tradities en smaakvolle bieren zijn nog steeds het avontuur waard, zelfs dichter bij huis.")
    
    andre_kyra = "https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/Andre_Kyra_bier.jpg.jpeg"
    st.image(andre_kyra, caption='Kijk ons genieten van het biertje!')
    
    st.write("")
    st.write("")
    st.subheader("VS vs EU:")
    st.write("Bekijk de verschillen tussen de VS en de EU. Hoe verschillen de biertjes met elkaar?")
    st.write("")
    st.subheader("Beer data per land en staat:")   
    st.write("Bekijk op een interactieve kaart hoe goed verschillende staten en landen scoren op het gebied van bier. Hier vind je gemiddelde beoordelingen en IBU-waardes (International Bitterness Units), zodat je direct kunt zien waar de beste bieren vandaan komen.")
    st.write("")
    st.subheader("Vind je favoriete bier:")
    st.write("Op zoek naar jouw perfecte biertje? Met behulp van een scatterplot en handige sliders kun je filteren op kenmerken zoals alcoholpercentage en bitterheid, zodat je precies vindt wat bij jouw smaak past.")
    st.write("")
    st.subheader("All beers:")
    st.write("Voor de liefhebbers die de volledige dataset willen verkennen: hier kun je door alle bieren bladeren, zoeken en filteren op basis van jouw voorkeuren.")
    st.write("")
    st.write("Duik in de wereld van bier en ontdek nieuwe favorieten met ons dashboard! 🍻")

############################################################################################################################
#
#       TAB 2 BOUWEN; EU vs VS
#
##############################################################################################################################

with tab2:

    st.title("De Grote Bierstrijd: VS vs. Europa 🍺🌍")
    st.write("In dit tabblad gaan we de strijd aangaan tussen de VS 🇺🇸 en Europa 🇪🇺! We vergelijken de biercijfers van beide continenten, van de populairste bierstijlen tot de ratings en alcoholpercentages. Met behulp van grafieken en plots krijg je een duidelijk overzicht van hoe de bierculturen zich verhouden. Laat de competitie beginnen! 🍻")

    # Bierstijlen per dataset groeperen
    amerikaans_bier_stijlen = amerikaansbier['sub_category_2_original'].value_counts()
    eu_bier_stijlen = eubier['sub_category_2_original'].value_counts()

    # Voeg "Overig" toe voor bierstijlen die minder dan 2% van de dataset uitmaken
    def categorize_bierstijlen(bier_stijlen):
        total = bier_stijlen.sum()
        threshold = 0.02 * total  # 2% van het totaal

        # Filter de bierstijlen die minder dan 2% zijn en voeg ze samen als 'Overig'
        categorized = bier_stijlen[bier_stijlen >= threshold]
        other = bier_stijlen[bier_stijlen < threshold].sum()
        
        # Voeg 'Overig' toe als de rest
        categorized['Overig'] = other
        return categorized

    # Categoriseer de bierstijlen voor beide datasets
    categorized_amerikaans_bier = categorize_bierstijlen(amerikaans_bier_stijlen)
    categorized_eu_bier = categorize_bierstijlen(eu_bier_stijlen)

    # Maak een subplot met 1 rij en 2 kolommen, en geef aan dat het pie charts zijn
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=["Soorten Bieren in Amerika", "Soorten Bieren in Europa"],
        specs=[[{'type': 'pie'}, {'type': 'pie'}]]  # Pie charts in beide kolommen
    )

    # Pie chart voor Amerika
    fig.add_trace(
        go.Pie(
            labels=categorized_amerikaans_bier.index,
            values=categorized_amerikaans_bier.values,
            hole=0.3,  # Maak het een donut chart
        ),
        row=1, col=1
    )

    # Pie chart voor Europa
    fig.add_trace(
        go.Pie(
            labels=categorized_eu_bier.index,
            values=categorized_eu_bier.values,
            hole=0.3,  # Maak het een donut chart
        ),
        row=1, col=2
    )

    # Layout aanpassen
    fig.update_layout(
        title_text="Soorten Bieren per Regio",
        showlegend=True,
        width=1000,  # Pas de breedte van de figuur aan
        height=500   # Pas de hoogte van de figuur aan
    )

    # Toon de grafiek in Streamlit
    st.plotly_chart(fig)





    ###################################### bar charts ##############################################

    st.header("Bierprofielenen:")

    # Voeg een kolom toe voor de regio (EU/VS)
    eubier['continent'] = 'EU'
    amerikaansbier['continent'] = 'US'

    # Combineer de datasets
    bier_combi_data = pd.concat([eubier, amerikaansbier], ignore_index=True)

    # Dropdown voor het kiezen van de metric (IBU, ABV, Beer Count)
    metric = st.selectbox(
        "Kies de metric voor de vergelijking",
        ("IBU", "ABV", "Aantal Bieren")
    )

    # Maak de figuur aan op basis van de gekozen metric
    fig = go.Figure()

    # Voeg een trace toe voor de EU en de VS
    if metric == "IBU":
        # Bereken de gemiddelde IBU per bierstijl voor de EU en de VS
        eu_avg_ibu = bier_combi_data[bier_combi_data['continent'] == 'EU'].groupby('sub_category_2_original')['ibu'].mean()
        us_avg_ibu = bier_combi_data[bier_combi_data['continent'] == 'US'].groupby('sub_category_2_original')['ibu'].mean()

        # EU IBU
        fig.add_trace(go.Bar(
            x=eu_avg_ibu.index,
            y=eu_avg_ibu.values,
            name='EU IBU',
            marker_color='blue'
        ))

        # US IBU
        fig.add_trace(go.Bar(
            x=us_avg_ibu.index,
            y=us_avg_ibu.values,
            name='US IBU',
            marker_color='red'
        ))

    elif metric == "ABV":
        # Bereken de gemiddelde ABV per bierstijl voor de EU en de VS
        eu_avg_abv = bier_combi_data[bier_combi_data['continent'] == 'EU'].groupby('sub_category_2_original')['abv'].mean()
        us_avg_abv = bier_combi_data[bier_combi_data['continent'] == 'US'].groupby('sub_category_2_original')['abv'].mean()

        # EU ABV
        fig.add_trace(go.Bar(
            x=eu_avg_abv.index,
            y=eu_avg_abv.values,
            name='EU ABV',
            marker_color='blue'
        ))

        # US ABV
        fig.add_trace(go.Bar(
            x=us_avg_abv.index,
            y=us_avg_abv.values,
            name='US ABV',
            marker_color='red'
        ))

    else:  # Aantal bieren
        # Bereken het aantal bieren per bierstijl voor de EU en de VS
        eu_beer_count = bier_combi_data[bier_combi_data['continent'] == 'EU'].groupby('sub_category_2_original')['name'].count()
        us_beer_count = bier_combi_data[bier_combi_data['continent'] == 'US'].groupby('sub_category_2_original')['name'].count()

        # EU Beer Count
        fig.add_trace(go.Bar(
            x=eu_beer_count.index,
            y=eu_beer_count.values,
            name='EU Beer Count',
            marker_color='blue'
        ))

        # US Beer Count
        fig.add_trace(go.Bar(
            x=us_beer_count.index,
            y=us_beer_count.values,
            name='US Beer Count',
            marker_color='red'
        ))

    # Layout van de grafiek
    fig.update_layout(
        title=f"Vergelijking van {metric} tussen EU en US",
        xaxis_title="Bierstijl",
        yaxis_title=metric,
        barmode='group',
        xaxis=dict(tickangle=45),  # Rotatie van de x-as labels
        height=600
    )

    # Toon de grafiek in de Streamlit app
    st.plotly_chart(fig)



############################################################################################################################
#
#       TAB 3 BOUWEN; KAARTEN
#
##############################################################################################################################


with tab3:

    st.title("De Ultieme Beer Kaart: Vindt Ratings, Bitterheid & Meer! 🍻🗺️")
    st.write("Hieronder is het mogelijk om met een dropdown menu een keuze te maken in de visualisatie, die jij wilt zien! Bekijk welk land het bitterste bier drinkt, het koudste bier drinkt, of wie het slechtste kan brouwen.")

    st.header("Alles op een rijtje:")

    ########### country naam vervangen met state, zodat makkelijker te combineren ################
    eubier = eubier.rename(columns={"country": "state", "ibu":"IBU"})
    europakaart = europakaart.rename(columns={"NAME": "state"})

    ############### Variabelen per EU staat maken ###########################
    # Gemiddelde rating per land
    ratingland = eubier.groupby('state')['rating'].mean().round(1)

    aantalbierperland = eubier.groupby('state').size().reset_index(name='aantal')
    # Gemiddelde IBU per land
    IBUland = eubier.groupby('state')['IBU'].mean().round(0)
    aantalbiermetIBU_land = eubier.groupby('state')['IBU'].count()

    # EU bier data combineren met de GJSON data
    ratingkaart_eu = europakaart.merge(ratingland, on='state', how='left')
    ratingkaart_eu = ratingkaart_eu.merge(aantalbierperland, on='state', how='left')

    IBUkaart_eu = europakaart.merge(IBUland, on='state', how='left')
    IBUkaart_eu = IBUkaart_eu.merge(aantalbiermetIBU_land, on='state', how='left')
    IBUkaart_eu = IBUkaart_eu.rename(columns={"IBU_x": "IBU", "IBU_y": 'aantal'})

    aantalkaart_eu = europakaart.merge(aantalbierperland, on='state', how='left')

    # Variabelen per US staat maken
    ratingstaat = amerikaansbier.groupby('state')['rating'].agg('mean').round(1)
    IBUstaat = amerikaansbier.groupby('state')['ibu'].agg('mean').round(0)
    aantalbiermetrating = amerikaansbier.groupby('state')['rating'].count()
    aantalbiermetIBU= amerikaansbier.groupby('state')['ibu'].count()
    aantalbierperstaat = amerikaansbier.groupby('state').size().reset_index(name='aantal')

    # Je wilt de 2 nieuwe variabelen samenvoegen met polygonenkaart. Daarvoor moeten de kolommen hetzelfde heten.
    # Het makkelijkst is om de naam van de kolom in de  GeoJson file te veranderen van 'name' naar 'state'
    statenkaart = statenkaart.rename(columns={"name": "state"})

    # Nu kun je die file samenvoegen met de aangemaakte variabelen. 
    # Je krijgt dan 2 kolommen extra met in de ene de rating per staat en in de andere het aantal biertjes met een rating.
    # De kolommen moet je nog weer even een logische naam geven, anders heten ze rating_x en rating_y.
    ratingkaart = statenkaart.merge(ratingstaat, on='state')
    ratingkaart = ratingkaart.merge(aantalbiermetrating, on='state')
    ratingkaart = ratingkaart.rename(columns={"rating_x": "rating", "rating_y": 'aantal'})

    IBUkaart = statenkaart.merge(IBUstaat, on='state')
    IBUkaart = IBUkaart.merge(aantalbiermetIBU, on='state')
    IBUkaart = IBUkaart.rename(columns={"ibu_x": "IBU", "ibu_y": 'aantal'})

    aantalkaart = statenkaart.merge(aantalbierperstaat, on='state')

    # EU en US datasets combineren
    ratingkaart_combi = pd.concat([ratingkaart, ratingkaart_eu], ignore_index=True)
    IBUkaart_combi = pd.concat([IBUkaart, IBUkaart_eu], ignore_index=True)
    aantalkaart_combi = pd.concat([aantalkaart, aantalkaart_eu], ignore_index=True)

    # Function to style polygons (transparent fill, but visible border)
    def style_function(feature):
        return {
            "fillColor": "transparent",  # Maakt de polygon transparant
            "color": "black",  # Zwarte randen zodat staten zichtbaar blijven
            "weight": 1,  # Dunne randen
            "fillOpacity": 0,  # Geen kleurvulling
        }

    ##################################################################
    # 
    # KAARTJE 1: RATINGPLOT
    # 
    ##################################################################
    
    CombiRatingPlot = folium.Map(location=[45.076401, -40.155497], zoom_start=2.5)

    folium.Choropleth(
        geo_data=ratingkaart_combi,
        name='geometry',
        data=ratingkaart_combi,
        columns=['state', 'rating'],
        key_on='feature.properties.state',
        fill_color='RdYlGn',
        fill_opacity=0.5,
        line_opacity=1,
        legend_name='Average Beer Rating (US & EU)'
    ).add_to(CombiRatingPlot)

    folium.GeoJson(
        ratingkaart_combi,
        name="States & Countries",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["state", "rating", 'aantal'],
            aliases=["State/Country:", "Average Beer Rating:", 'No of Beers:'],
            localize=True,
            sticky=False
        ),
        popup=folium.GeoJsonPopup(
            fields=["state", "rating", 'aantal'],
            aliases=["State/Country:", "Average Beer Rating:", 'No of Beers:']
        )
    ).add_to(CombiRatingPlot)

    folium.LayerControl().add_to(CombiRatingPlot)

    ##################################################################
    # 
    # KAARTJE 2: IBUPLOT
    # 
    ##################################################################
    CombiIBUPlot = folium.Map(location=[45.076401, -40.155497], zoom_start=2.5)

    folium.Choropleth(
        geo_data=IBUkaart_combi,
        name='geometry',
        data=IBUkaart_combi,
        columns=['state', 'IBU'],
        key_on='feature.properties.state',
        fill_color='Blues',
        fill_opacity=0.5,
        line_opacity=1,
        legend_name='Average IBU Score (US & EU)'
    ).add_to(CombiIBUPlot)

    folium.GeoJson(
        IBUkaart_combi,
        name="States & Countries",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["state", "IBU", 'aantal'],
            aliases=["State/Country:", "Average IBU Score:", 'No of Beers:'],
            localize=True,
            sticky=False
        ),
        popup=folium.GeoJsonPopup(
            fields=["state", "IBU", 'aantal'],
            aliases=["State/Country:", "Average IBU Score:", 'No of Beers:']
        )
    ).add_to(CombiIBUPlot)

    folium.LayerControl().add_to(CombiIBUPlot)

    ##################################################################
    # 
    # KAARTJE 3: NO OF BEERS KAARTJE
    # 
    ##################################################################

    CombiAantalPlot = folium.Map(location=[45.076401, -40.155497], zoom_start=2.5)

    folium.Choropleth(
        geo_data=aantalkaart_combi,
        name='geometry',
        data=aantalkaart_combi,
        columns=['state', 'aantal'],
        key_on='feature.properties.state',
        fill_color='Greens',
        fill_opacity=0.5,
        line_opacity=1,
        legend_name='Number of different beers (US & EU)'
    ).add_to(CombiAantalPlot)

    folium.GeoJson(
        aantalkaart_combi,
        name="States & Countries",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["state", 'aantal'],
            aliases=["State/Country:", 'No of different beers:'],
            localize=True,
            sticky=False
        ),
        popup=folium.GeoJsonPopup(
            fields=["state", 'aantal'],
            aliases=["State/Country:", 'No of different beers:']
        )
    ).add_to(CombiAantalPlot)

    folium.LayerControl().add_to(CombiAantalPlot)

    ########################################################################################

    # KAARTJE 4: TEMPERATUREN

    ########################################################################################
    # Functie om de gemiddelde temperatuur uit de range te halen
    def extract_average_temp(temp_range):
        # Splits de string in twee delen en bereken het gemiddelde
        try:
            start_temp, end_temp = temp_range.split('-')
            start_temp = float(start_temp)
            end_temp = float(end_temp.replace('° C', ''))
            return (start_temp + end_temp) / 2
        except:
            return None  # In geval van een lege of ongeldige waarde

    # Verwerk de temperatuurdata voor beide datasets
    eubier['avg_temp'] = eubier['serving_temp_c'].apply(extract_average_temp)
    amerikaansbier['avg_temp'] = amerikaansbier['serving_temp_c'].apply(extract_average_temp)

    # Gemiddelde temperatuur per staat (EU)
    avg_temp_eu = eubier.groupby('state')['avg_temp'].mean().round(1)

    # Gemiddelde temperatuur per staat (VS)
    avg_temp_us = amerikaansbier.groupby('state')['avg_temp'].mean().round(1)

    # Voeg de temperatuurdata samen met de geopandas data voor EU en VS
    # EU
    ratingkaart_eu_temp = europakaart.merge(avg_temp_eu, on='state', how='left')

    # VS
    statenkaart_temp = statenkaart.merge(avg_temp_us, on='state', how='left')

    # Combineer de EU en US gegevens
    tempkaart_combi = pd.concat([ratingkaart_eu_temp, statenkaart_temp], ignore_index=True)

    # Maak de folium kaart
    CombiTempPlot = folium.Map(location=[45.076401, -40.155497], zoom_start=2.5)

    # Voeg de choropleth toe voor gemiddelde serveertemperatuur
    folium.Choropleth(
        geo_data=tempkaart_combi,
        name='geometry',
        data=tempkaart_combi,
        columns=['state', 'avg_temp'],
        key_on='feature.properties.state',
        fill_color='Blues',  
        fill_opacity=0.5,
        line_opacity=1,
        legend_name='Average Serving Temperature (°C)'
    ).add_to(CombiTempPlot)

    # Voeg een GeoJSON toe voor interactieve tooltips en popups
    folium.GeoJson(
        tempkaart_combi,
        name="States & Countries",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["state", "avg_temp"],
            aliases=["State/Country:", "Average Serving Temperature (°C):"],
            localize=True,
            sticky=False
        ),
        popup=folium.GeoJsonPopup(
            fields=["state", "avg_temp"],
            aliases=["State/Country:", "Average Serving Temperature (°C):"]
        )
    ).add_to(CombiTempPlot)

    # Voeg de laagcontrole toe
    folium.LayerControl().add_to(CombiTempPlot)

    ################################ KPI TABS TOEVOEGEN ############################################
    # Bereken KPI's voor Europa
    eu_land_meeste_bieren = eubier['state'].value_counts().idxmax()
    eu_land_hoogste_ibu = eubier.groupby('state')['IBU'].mean().idxmax()
    eu_land_hoogste_rating = eubier.groupby('state')['rating'].mean().idxmax()
    eu_land_koudste_bier = eubier.groupby('state')['avg_temp'].mean().idxmin()

    # Bereken KPI's voor de VS
    us_staat_meeste_bieren = amerikaansbier['state'].value_counts().idxmax()
    us_staat_hoogste_ibu = amerikaansbier.groupby('state')['ibu'].mean().idxmax()
    us_staat_hoogste_rating = amerikaansbier.groupby('state')['rating'].mean().idxmax()
    us_staat_koudste_bier = amerikaansbier.groupby('state')['avg_temp'].mean().idxmin()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="EU Land met meeste bieren", value=eu_land_meeste_bieren)
        st.metric(label="EU Land met hoogste IBU", value=eu_land_hoogste_ibu)
        st.metric(label="EU Land met hoogste rating⭐", value=eu_land_hoogste_rating)
        st.metric(label="EU Land met koudste bier🌡️", value=eu_land_koudste_bier)

    with col2:
        st.metric(label="VS Staat met meeste bieren", value=us_staat_meeste_bieren)
        st.metric(label="VS Staat met hoogste IBU", value=us_staat_hoogste_ibu)
        st.metric(label="VS Staat met hoogste rating⭐", value=us_staat_hoogste_rating)
        st.metric(label="VS Staat met koudste bier🌡️", value=us_staat_koudste_bier)


    # Selectbox voor keuze van de kaart
    keuze = st.selectbox("Selecteer de plot", ("Lokale biertjes per staat", "IBUs per staat", "Rating per staat", "Gemiddelde bier temperatuur"))

    # Functie om juiste kaart weer te geven
    if keuze == "Lokale biertjes per staat":
        kaart = CombiAantalPlot
        beschrijving = "Deze interactieve kaart toont het aantal unieke bieren per Amerikaanse staat en Europees land. Ontdek welke regio’s een rijke biercultuur hebben en waar de meeste verschillende bieren worden gebrouwen. Hoe donkerder de kleur, hoe meer biervarianten er beschikbaar zijn. Proost! 🍻"
    elif keuze == "IBUs per staat":
        kaart = CombiIBUPlot
        beschrijving = "Deze kaart laat de gemiddelde International Bitterness Units (IBU) per Amerikaanse staat en Europees land zien. De IBU-waarde geeft aan hoe bitter een bier is – hoe hoger de waarde, hoe meer hop en bitterheid je kunt verwachten. Donkere gebieden hebben gemiddeld bittere bieren, terwijl lichtere regio’s mildere smaken bieden. 🍺"
    elif keuze == "Rating per staat":
        kaart = CombiRatingPlot
        beschrijving = "Deze kaart toont de gemiddelde bierbeoordeling per Amerikaanse staat en Europees land. De kleurintensiteit geeft aan hoe hoog de gemiddelde rating is – donkere gebieden hebben beter beoordeelde bieren, terwijl lichtere regio’s gemiddeld lagere scores krijgen. Voor de Europese landen ontbrak bij veel bieren een rating. Om deze aan te vullen, is een Random Forest Regressor gebruikt, waarmee de ontbrekende ratings zijn voorspeld op basis van andere bierkenmerken. De **Mean Absolute Error** (MAE) van dit model was **0.09**, wat betekent dat de voorspelde ratings zeer dicht bij de echte waarden liggen. Hierdoor ontstaat een vollediger en betrouwbaarder beeld van bierbeoordelingen in Europa! 🍻⭐"
    elif keuze == "Gemiddelde bier temperatuur":
        kaart = CombiTempPlot
        beschrijving = "Deze kaart toont de gemiddelde serveertemperatuur van bier per Amerikaanse staat en Europees land. De kleurintensiteit geeft aan hoe warm of koud bieren in een regio doorgaans worden geserveerd. In sommige landen worden bieren traditioneel warmer gedronken, zoals bepaalde ales en stouts in Europa, terwijl in andere regio’s, zoals de VS, veel bieren juist ijskoud worden geserveerd. De temperatuurdata is gebaseerd op de aanbevolen serveertemperaturen van bieren uit de dataset. Dit geeft een interessant inzicht in de biercultuur en drinkgewoonten wereldwijd! 🍺❄🔥"

    st.write(beschrijving)

    # Toon de juiste kaart
    st_folium(kaart, width=1500, height=800)

    #################
    # st.plotly_chart(fig)

##############################################################################
#
#           TAB 4 BOUWEN; SCATTER PLOTS
#
##################################################################################

with tab4:

    st.header("Jouw favoriete bier onder de loep! Meer bitter of meer alcohol? 🔍🍻 ")
    st.write("Kijk hier welk biertje het beste bij jouw past! Kijk op basis van het alcohol percentage en IBU score welke bieren, uit welke landen het beschikbaar zijn.")

    # Unieke kleuren per staat/land
    unique_states = sorted(amerikaansbier["state"].unique())  
    state_color_map = {state: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, state in enumerate(unique_states)}

    unique_countries = sorted(eubier["state"].unique())  
    country_color_map = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, country in enumerate(unique_countries)}

    # ---- 1. Maak een lege container voor de grafieken ----
    graph_placeholder = st.empty()

    # ---- 2. Plaats de sliders boven de grafiek ----
    values = st.slider(
        "Selecteer een IBU-bereik", 
        int(min(amerikaansbier["ibu"].min(), eubier["IBU"].min())),  
        int(max(amerikaansbier["ibu"].max(), eubier["IBU"].max())),  
        (20, 80)
    )

    values2 = st.slider(
        "Selecteer een Alcoholpercentage", 
        float(min(amerikaansbier["abv"].min(), eubier["abv"].min())),  
        float(max(amerikaansbier["abv"].max(), eubier["abv"].max())),  
        (0.0, 10.0),
        step=0.5
    )

    values3 = st.slider(
        "Selecteer een Rating-bereik",
        float(min(amerikaansbier["rating"].min(), eubier["rating"].min())),
        float(max(amerikaansbier["rating"].max(), eubier["rating"].max())),
        (3.0, 5.0),
        step=0.5
    )

    # ---- 3. Filter de data op basis van de slider ----
    filtered_amerikaansbier = amerikaansbier[
        (amerikaansbier["ibu"] >= values[0]) & (amerikaansbier["ibu"] <= values[1]) &
        (amerikaansbier["abv"] >= values2[0]) & (amerikaansbier["abv"] <= values2[1]) &
        (amerikaansbier["rating"] >= values3[0]) & (amerikaansbier["rating"] <= values3[1])
    ]

    filtered_eubier = eubier[
        (eubier["IBU"] >= values[0]) & (eubier["IBU"] <= values[1]) &
        (eubier["abv"] >= values2[0]) & (eubier["abv"] <= values2[1]) &
        (eubier["rating"] >= values3[0]) & (eubier["rating"] <= values3[1])
    ]

    # ---- 4. Maak de Amerikaanse scatterplot ----
    fig_us = go.Figure()
    for state in unique_states:
        df_state = filtered_amerikaansbier[filtered_amerikaansbier["state"] == state]
        
        fig_us.add_trace(go.Scatter(
            x=df_state["ibu"],  
            y=df_state["abv"],
            mode="markers",
            marker=dict(color=state_color_map[state]),
            name=state,  
            text=df_state.apply(lambda row: f"Naam: {row['name']}<br>"
                                  f"Brouwer: {row['brewery_original']}<br>"
                                  f"Type: {row['sub_category_2_original']}<br>"
                                  f"ABV: {row['abv']}%<br>"
                                  f"{'IBU: ' + str(row['ibu']) if pd.notna(row['ibu']) else ''}", axis=1),
            hoverinfo='text',
            visible="legendonly" if unique_states.index(state) >= 3 else True  
        ))

    fig_us.update_layout(
        title="Alcoholpercentage vs Bitterheid (VS)",
        xaxis_title="IBU (Bitterheid)",
        yaxis_title="ABV (Alcoholpercentage)",
        template="plotly_white",
        legend_title="State",
        xaxis=dict(range=[0, 100]),  
        yaxis=dict(range=[0, 18]),   
        width=600,  
        height=500  
    )

    # ---- 5. Maak de Europese scatterplot ----
    fig_eu = go.Figure()
    for country in unique_countries:
        df_country = filtered_eubier[filtered_eubier["state"] == country]
        
        fig_eu.add_trace(go.Scatter(
            x=df_country["IBU"],  
            y=df_country["abv"],
            mode="markers",
            marker=dict(color=country_color_map[country]),
            name=country,  
            text=df_country.apply(lambda row: f"Naam: {row['name']}<br>"
                                  f"Brouwer: {row['brewery_original']}<br>"
                                  f"Type: {row['sub_category_2_original']}<br>"
                                  f"ABV: {row['abv']}%<br>"
                                  f"{'IBU: ' + str(row['IBU']) if pd.notna(row['IBU']) else ''}", axis=1),
            hoverinfo='text',
            visible="legendonly" if unique_countries.index(country) >= 3 else True  
        ))

    fig_eu.update_layout(
        title="Alcoholpercentage vs Bitterheid (EU)",
        xaxis_title="IBU (Bitterheid)",
        yaxis_title="ABV (Alcoholpercentage)",
        template="plotly_white",
        legend_title="Country",
        xaxis=dict(range=[0, 100]),  
        yaxis=dict(range=[0, 18]),   
        width=600,  
        height=500  
    )

    # ---- 6. Toon beide grafieken naast elkaar in Streamlit ----
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_us)

    with col2:
        st.plotly_chart(fig_eu)

##############################################################################
#
#           TAB 5 BOUWEN; FOOD PAIRINGS
#
##################################################################################

with tab5:

    allebiertabel_us = amerikaansbier[['name', 'brewery_original', 'rating', 'sub_category_2_original','food_pairing']]
    allebiertabel_eu = eubier[['name', 'brewery_original', 'rating', 'sub_category_2_original','food_pairing']]

    # Verwijder NaN waarden of vervang ze door een lege string
    allebiertabel_us['sub_category_2_original'] = allebiertabel_us['sub_category_2_original'].fillna('')
    eubier['sub_category_2_original'] = eubier['sub_category_2_original'].fillna('')

    # Beschikbare keuzes voor food pairing en bierstijl
    available_foods = ["chicken", "beef", "pork", "seafood", "salad", "cheese", "dessert", "spicy", "fruit"]
    available_beer_styles = sorted(list(set(allebiertabel_us['sub_category_2_original'].unique()).union(eubier['sub_category_2_original'].unique())))

    # Streamlit UI
    st.header("Bekijk welk biertje bij jouw eten past! 🍻")
    st.write("Welkom bij de food pairing functie! 🍽️🍻 Selecteer eenvoudig het eten waar je zin in hebt, en ontdek welk bier er perfect bij past. Of je nu kiest voor een sappige steak 🥩, een frisse salade 🥗, of een pittig gerecht 🌶️, wij helpen je het ideale bier te vinden om je maaltijd compleet te maken!")

    # Keuze voor dataset
    dataset_choice = st.selectbox("Kies je bier regio", ["Amerikaans", "Europees"])

    # Bepaal het juiste DataFrame op basis van de keuze
    if dataset_choice == "Amerikaans":
        bier_data = allebiertabel_us
    elif dataset_choice == "Europees":
        bier_data = allebiertabel_eu

    # Multiselect widget voor food pairing
    selected_foods = st.multiselect("Zoeken op food pairing", available_foods)

    # Multiselect widget voor bierstijl
    selected_styles = st.multiselect("Zoeken op bierstijl", available_beer_styles)

    # Filtering op food pairing
    if selected_foods:
        filtered_df = allebiertabel_us[allebiertabel_us['food_pairing'].apply(lambda x: any(food in x for food in selected_foods))]
    else:
        filtered_df = allebiertabel_us  # Toon alles als er geen selectie is

    # Filtering op bierstijl
    if selected_styles:
        filtered_df = filtered_df[filtered_df['sub_category_2_original'].isin(selected_styles)]

    # Namen aanpassen
    filtered_df = filtered_df.rename(columns={
        'name': 'Bier naam',
        'brewery_original':'Brouwerij',
        'sub_category_2_original': 'Bierstijl',
        'food_pairing': 'Passend eten'
    })

    # Weergeven van het gefilterde DataFrame
    st.dataframe(filtered_df[['Bier naam', 'Brouwerij', 'rating', 'Bierstijl', 'Passend eten']])

##############################################################################
#
#           TAB 6 BOUWEN; UPDATE LOG
#
##################################################################################

with tab6:
    st.title("Update-Log 1.1")
    st.header("home of beer:")
    st.write("- Nerative van het dashboard veranderd... Trump is een eikel.")
    st.write("")
    st.header("VS vs EU:")
    st.write("- **NIEUW**, analyse over hoe Amerika presteert tegenover Europa!")
    st.header("Beermap:")
    st.write("- Europa toegevoegd!")
    st.write("- KPI tab toegevoegd!")
    st.write("- Per kaart een stukje toegevoegd wat de kaart laat zien!")
    st.write("- Kleur van de rating aangepast zodat hogere rating niet meer rood is gekleurd!:")

    oud_rating = 'https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/oud_rating_kaart.png'
    st.image(oud_rating, caption="Boven nieuw, onder oud.")

    st.write("- Kaart toegevoegd waarin per land/staat de gemiddelde temp. van bieren te zien is!")

    kaart_temp = 'https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/kaart_temp.png'
    st.image(kaart_temp, caption="Nieuwe temperatuur kaart!.")

    st.write("")
    st.header("Find Your Favorite Beer:")
    st.write("- Uitgebreid met Europa!")
    st.write("- Labels uitgebreid met info over het type bier!")

    oud_label = 'https://raw.githubusercontent.com/CoderendeAziaat/beerdash/main/oud_nieuw_label.png'
    st.image(oud_label, caption="Boven oud, onder nieuw")

    st.write("")
    st.write("- Stapgrootte aangepast van de ABV slider")

    st.write("")
    st.header("Coldest Beer Destinations ")
    st.write("- Verwijderd")
    st.write("")
    st.header("All beers:")
    st.write("- Veranderd naar food-pairings")
    st.write("- Uitgebreid met Europa!")
