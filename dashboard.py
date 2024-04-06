import streamlit as st
import pandas as pd
import altair as alt

# Define the path to the logos directory
logos_path = "logos"


# Function to normalize and count categories
def normalize_and_count_categories(df, column_name):
    # Normalize and split categories
    df[column_name] = df[column_name].str.upper()  # Convert to uppercase
    df[column_name] = df[column_name].str.replace(
        ";", ","
    )  # Replace semicolons with commas
    all_categories = df[column_name].str.split(",")  # Split categories
    all_categories = all_categories.explode()  # Transform list of categories into rows
    all_categories = all_categories.str.strip()  # Remove extra spaces
    all_categories = all_categories[all_categories != "OUTROS"]  # Remove 'Outros'
    # Count categories
    category_counts = all_categories.value_counts(normalize=True) * 100
    # Sort categories from highest to lowest
    category_counts = category_counts.sort_values(ascending=False)
    return category_counts.reset_index(name='Value')


# Function to handle button click for selecting a company
def selecionar_empresa(empresa):
    st.session_state.empresa_selecionada = empresa


# Initialize session state
if "empresa_selecionada" not in st.session_state:
    st.session_state["empresa_selecionada"] = None

# Load and process CSV file
df = pd.read_csv(
    "stream.csv",
    usecols=[
        "Nome da empresa",
        "Denúncia",
        "Em quais categorias sua denúncia se encaixa?",
    ],
)

# Normalize and count categories
categorias_contagem = normalize_and_count_categories(
    df, "Em quais categorias sua denúncia se encaixa?"
)

# Calculate the top 5 most mentioned companies
ranking_empresas = df["Nome da empresa"].value_counts().head(5)

# Set up the two-column layout
col1, col2 = st.columns([1, 3])

# Left column: Top 5 most mentioned companies with generic logo
with col1:
    st.subheader("Top 5 Empresas Mais Citadas")
    for empresa in ranking_empresas.index:
        if st.button(empresa, key=empresa):
            selecionar_empresa(empresa)

# Right column: Bar chart and complaints for the selected company or all companies
with col2:
    st.title("Dashboard de Denúncias Tóxicas em Empresas")
    if st.session_state.empresa_selecionada:
        # Filter complaints for the selected company and recalculate categories
        df_empresa = df[df["Nome da empresa"] == st.session_state.empresa_selecionada]
        categorias_contagem_empresa = normalize_and_count_categories(
            df_empresa, "Em quais categorias sua denúncia se encaixa?"
        )
        st.subheader(
            f"Categorias de Denúncias (%) - {st.session_state.empresa_selecionada}"
        )
        # Create the chart with the sorted DataFrame
        bar_chart = alt.Chart(categorias_contagem_empresa).mark_bar().encode(
            x=alt.X('Em quais categorias sua denúncia se encaixa?:N', sort=alt.EncodingSortField(field='Value', op='sum', order='ascending')),
            y=alt.Y('Value:Q')
        )

        st.altair_chart(bar_chart, use_container_width=True)
        st.subheader(f"Denúncias da Empresa: {st.session_state.empresa_selecionada}")
        for denuncia in df_empresa["Denúncia"]:
            st.text(denuncia)  # Exibir denúncia com quebra automática de linha
    else:
        # Display the chart with categories for all companies
        st.subheader("Categorias de Denúncias (%)")

        # Create the chart with the sorted DataFrame
        bar_chart = alt.Chart(categorias_contagem).mark_bar().encode(
            x=alt.X('Em quais categorias sua denúncia se encaixa?:N', sort=alt.EncodingSortField(field='Value', op='sum', order='ascending')),
            y=alt.Y('Value:Q')
        )

        st.altair_chart(bar_chart, use_container_width=True)
