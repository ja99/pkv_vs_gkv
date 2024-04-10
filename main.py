import streamlit as st
import plotly.express as px
import pandas as pd
import datetime

THIS_YEAR = datetime.datetime.now().year
A_HUNDRED_YEARS = THIS_YEAR + 100

# Title of the website
st.title('GKV vs PKV')

# x range
years_range = st.slider("Betrachtungszeitraum in Jahren:", THIS_YEAR, A_HUNDRED_YEARS, (THIS_YEAR, THIS_YEAR+75))

st.write("!!!!!BISHER FEHLT BEITRAGS BEMESSUNGSGRENZE!!!!!")
st.write("!!!!!KEINERLEI BETRACHTUNG VON INFLATION!!!!!")

# input fields
gkv_base = st.number_input('GKV Abschlag in % (brutto)', min_value=0.0, max_value=100.0, value=14.6)
gkv_additional = st.number_input('GKV Zusatzbeitrag in % (brutto)', min_value=0.0, max_value=100.0, value=1.3)
gkv_dental = st.number_input('GKV Zahnarzt in % (brutto)', min_value=0.0, max_value=100.0, value=1.0)

gkv_percent = (
        gkv_base * 0.5
        + gkv_additional * 0.5
        + gkv_dental # employer doesn't pay this
)

pkv_start = st.number_input('PKV Startkosten in Euro (netto)', min_value=0.0, max_value=1_000.0, value=480.0/2)

gkv_percent_increase = st.number_input('GKV Abschlag Erhöhung pro Jahr in %', min_value=0.0, max_value=100.0, value=3.3)
pkv_increase = st.number_input('PKV Erhöhung pro Jahr in %', min_value=0.0, max_value=100.0, value=2.6)

income_start = st.number_input('Einkommen Start in Euro', min_value=0.0, max_value=1_000_000.0, value=70_000.0)
income_increase = st.number_input('Einkommen Erhöhung pro Jahr in %', min_value=0.0, max_value=100.0, value=2.0)

# Don't forget the price increases for pkv for those two
pkv_cost_wife = st.number_input('PKV Kosten Ehefrau aktuell in Euro (steigt mit Preisanstieg in Prozent von oben)', min_value=0.0, max_value=1_000.0, value=600.0)
pkv_cost_child = st.number_input('PKV Kosten Kind aktuell in Euro (steigt mit Preisanstieg in Prozent von oben)', min_value=0.0, max_value=1_000.0, value=265.0)

pkv_pay_for_kids_till = st.number_input('PKV für Kinder zahlen bis Alter', min_value=18, max_value=30, value=25)

n_children = st.number_input('Anzahl Kinder', min_value=0, max_value=10, value=2)

child_birth_years = []
for i in range(n_children):
    child_birth_years.append(st.number_input(f'Kind {i+1} Geburtsjahr', min_value=THIS_YEAR, max_value=A_HUNDRED_YEARS, value=THIS_YEAR+5+ i*3))

wife_at_home_years = st.number_input('Ehefrau zu Hause ab Kind 1 in Jahre', min_value=0, max_value=10, value=3)

# Simulate costs
gkv_costs = []
pkv_costs = []
years = list(range(years_range[0], years_range[1]))
income = income_start
pkv_cost = pkv_start*12 # yearly cost
for year in years:
    # Calculate the GKV cost for the year
    gkv_cost = (income * gkv_percent) / 100
    gkv_costs.append(gkv_cost)

    # Calculate the PKV cost for the year
    pkv_total_cost = pkv_cost  # Start with base cost for the insured

    if len(child_birth_years) > 0:
        # Adjust for spouse PKV cost if within the years she's at home
        if child_birth_years[0] <= year <= child_birth_years[0] + wife_at_home_years:
            pkv_total_cost += pkv_cost_wife * 12 # yearly cost

        # Adjust for children PKV cost
        for birth_year in child_birth_years:
            if birth_year <= year <= birth_year+pkv_pay_for_kids_till:
                pkv_total_cost += pkv_cost_child*12 # yearly cost

    pkv_costs.append(pkv_total_cost)

    # Update for next year
    income *= 1 + (income_increase / 100)
    pkv_cost *= 1 + (pkv_increase / 100)
    pkv_cost_wife *= 1 + (pkv_increase / 100)
    pkv_cost_child *= 1 + (pkv_increase / 100)



# Creating a DataFrame for Plotly
df = pd.DataFrame({
    'x': list(range(years_range[0], years_range[1])),
    'gkv': gkv_costs,
    'pkv': pkv_costs,
    "income": [income_start * (1 + income_increase / 100) ** (year - years_range[0]) for year in years],
    "cum_gkv": [sum(gkv_costs[:i+1]) for i in range(len(gkv_costs))],
    "cum_pkv": [sum(pkv_costs[:i+1]) for i in range(len(pkv_costs))],
})

# Creating a line plot using Plotly with two lines
fig_yearly = px.line(df, x='x')
fig_yearly.add_scatter(x=df['x'], y=df['gkv'], mode='lines', name='GKV')
fig_yearly.add_scatter(x=df['x'], y=df['pkv'], mode='lines', name='PKV')
fig_yearly.add_scatter(x=df['x'], y=df['income'], mode='lines', name='Einkommen', visible='legendonly')
fig_yearly.update_layout(title='GKV vs PKV Kosten', xaxis_title='Jahr', yaxis_title='Kosten in Euro')

st.plotly_chart(fig_yearly)

# Creating a line plot using Plotly with two lines
fig_cum = px.line(df, x='x')
fig_cum.add_scatter(x=df['x'], y=df['cum_gkv'], mode='lines', name='Kumulierte GKV Kosten')
fig_cum.add_scatter(x=df['x'], y=df['cum_pkv'], mode='lines', name='Kumulierte PKV Kosten')
fig_cum.add_scatter(x=df['x'], y=df['income'], mode='lines', name='Einkommen (nicht kumuliert)')
fig_cum.update_layout(title='GKV vs PKV Kosten kumulativ', xaxis_title='Jahr', yaxis_title='Kosten in Euro')

st.plotly_chart(fig_cum)




