import pandas as pd
import streamlit as st
from datetime import datetime
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Wilde',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare functions.

@st.cache_data
def get_sales():
    """Grab data from a CSV file."""
    DATA_FILENAME = r'true_sales_cust.csv'
    sales = pd.read_csv(DATA_FILENAME)

    sales['date'] = pd.to_datetime(sales['date'])

    sales = sales[sales.status=='closed'].groupby(
        [pd.Grouper(key='date', freq='W'), 'cust_parent_name']
    ).agg({'amount': 'sum'}).reset_index().astype({'amount': 'int64', 'cust_parent_name': 'string'})

    return sales

sales = get_sales()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Welcome to [Wilde](https://www.wildebrands.com/).
'''

# Add some spacing
''
''

# Convert min and max dates to datetime.datetime
min_value = sales.date.min().to_pydatetime()
max_value = sales.date.max().to_pydatetime()

from_date, to_date = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=(min_value, max_value)
)

parent_customers = sorted(sales['cust_parent_name'].unique())

if not len(parent_customers):
    st.warning("Select at least one Parent Customer")

# get top 10 parent_customers by sales
parent_customers_to_show = sales[
    sales.date.dt.year > 2024
    ].groupby(
        'cust_parent_name'
        ).agg({'amount':'sum'}
              ).sort_values('amount',ascending=False
                            ).head(10).index.tolist()

selected_parent_customers = st.multiselect(
    'Which parent_customers would you like to view?',
    parent_customers,
    parent_customers_to_show)

''
''
''

# Filter the data
filtered_sales = sales[
    (sales['cust_parent_name'].isin(selected_parent_customers))
    & (sales['date'] <= to_date)
    & (from_date <= sales['date'])
]

st.header('Sales over time', divider='gray')

''

import plotly.express as px

line_chart = px.line(
    filtered_sales,
    x='date',
    y='amount',
    color='cust_parent_name',
).update_layout(showlegend=False)

st.plotly_chart(line_chart,
    use_container_width=True,
)

''
''


first_date = sales[sales['date'] == from_date]
last_date = sales[sales['date'] == to_date]

st.header(f'YoY by Customer', divider='gray')

''

cols = st.columns(4)

for i, parent_customer in enumerate(selected_parent_customers):
    col = cols[i % len(cols)]

    with col:
        first_parent_cust = first_date[sales['cust_parent_name'] == parent_customer]['amount'].sum() / 1_00
        last_parent_cust = last_date[sales['cust_parent_name'] == parent_customer]['amount'].sum() / 1_00

        if math.isnan(first_parent_cust):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_parent_cust - first_parent_cust:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{parent_customer}',
            value=f'{last_parent_cust:,.0f}K',
            delta=growth,
            delta_color=delta_color
        )