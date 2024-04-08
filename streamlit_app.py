import streamlit as st
import pandas as pd
import altair as alt
import unicodedata

caminho_do_logotipo = "logos/exposedworkplacesbig.png"

# Lista de categorias válidas
valid_categories = [
    "DIVERSIDADE",
    "ASSÉDIO(MORAL/SEXUAL)",
    "MICROGERENCIAMENTO",
    "SALÁRIO/BENEFÍCIOS",
    "COMUNICAÇÃO/TRANSPARÊNCIA",
    "POSSIBILIDADE DE CRESCIMENTO",
    "SEGURANÇA/SAÚDE",
    "FERRAMENTAS DE TRABALHO",
    "LIDERANÇA TÓXICA",
    "CARGA DE TRABALHO EXCESSIVA",
]

# Initialize session state
st.set_page_config(layout="wide", page_title="Exposed Workplaces", page_icon="📊")
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

# Aplicar a remoção de acentos e conversão para minúsculas na coluna "Nome da empresa"
df["Nome da empresa"] = (
    df["Nome da empresa"]
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
)
df["Nome da empresa"] = df["Nome da empresa"].str.lower()


# Função para remover acentos de uma string
def remover_acentos(txt):
    return unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")


# Function to normalize and count categories
def normalize_and_count_categories(df, column_name, include_others=False):
    # Normalize and split categories
    df[column_name] = df[column_name].str.upper()  # Convert to uppercase
    df[column_name] = df[column_name].str.replace(
        ";", ","
    )  # Replace semicolons with commas
    all_categories = df[column_name].str.split(",")  # Split categories
    all_categories = all_categories.explode()  # Transform list of categories into rows
    all_categories = all_categories.str.strip()  # Remove extra spaces

    if include_others:
        # Filtrar somente as categorias válidas e contar, incluindo "OUTROS"
        all_categories = all_categories.apply(
            lambda x: x if x in valid_categories else "OUTROS"
        )
    else:
        # Manter apenas as categorias que estão em valid_categories
        all_categories = all_categories[all_categories.isin(valid_categories)]

    category_counts = all_categories.value_counts(normalize=True) * 100
    category_counts = category_counts.sort_values(ascending=False)
    return category_counts.reset_index(name="Value")


# Function to handle button click for selecting a company
def selecionar_empresa(empresa):
    print("Empresas", empresa)
    st.session_state.empresa_selecionada = [e for e in empresa]


# Initialize session state
if "empresa_selecionada" not in st.session_state:
    st.session_state["empresa_selecionada"] = None

st.title("As Empresas mais Tóxicas do Brasil ☣️")
# Normalize and count categories
categorias_contagem = normalize_and_count_categories(
    df, "Em quais categorias sua denúncia se encaixa?"
)

# Calculate the top 5 most mentioned companies
ranking_empresas = df["Nome da empresa"].value_counts().head(5)

denuncias_por_empresa = df["Nome da empresa"].value_counts().reset_index()
denuncias_por_empresa.columns = ["Nome da empresa", "Quantidade de Denúncias"]

# Filtrar para as top 10 empresas com maior número de denúncias
top_10_denuncias_por_empresa = denuncias_por_empresa.head(10)

# Criar o Gráfico de Barras com Altair para as top 10 empresas
chart_top_10_empresas = (
    alt.Chart(top_10_denuncias_por_empresa)
    .mark_bar(color="red")
    .encode(
        x=alt.X("Nome da empresa:N", sort="-y", title="Empresas"),
        y=alt.Y("Quantidade de Denúncias:Q", title="Quantidade de Denúncias"),
        tooltip=["Nome da empresa", "Quantidade de Denúncias"],
    )
    .properties(width=600)  # Ajuste a largura conforme necessário
)

# Inserir o Gráfico na Página
st.subheader("Top 10 Empresas com Maior Número de Denúncias")
st.altair_chart(chart_top_10_empresas, use_container_width=True)


def reset_multiselect_companies():
    print("pediu pra limpar")
    st.session_state.multiselectcompanies = []


# Left column: Top 5 most mentioned companies with generic logo
with st.sidebar:

    # Exibe o logotipo na barra lateral
    st.image(caminho_do_logotipo, use_column_width=True)
    st.title("Dashboard de Denúncias Tóxicas em Empresas")

    # Limpar Seleção na linha 118
    if st.button("Limpar Seleção", type="primary"):
        reset_multiselect_companies()
        st.session_state.empresa_selecionada = None
        st.experimental_rerun()

    empresas = st.multiselect(
        "Filtrar por Empresa",
        df["Nome da empresa"].unique(),
        key="multiselectcompanies",
        help="Selecione as empresas que quer ver no gráfico ao lado.",
        max_selections=5,
    )
    if empresas:
        selecionar_empresa(empresas)

    categorias = st.multiselect(
        "Filtrar por Categoria",
        valid_categories,  # Usando sua lista pré-definida de categorias válidas
        key="multiselectcategories",
        help="Selecione uma ou mais categorias para filtrar.",
        max_selections=5,
    )

    # Suponha que esta função esteja definida em algum lugar no seu script
    def calcular_porcentagem_denuncias_por_empresa_categoria(df, categoria_escolhida):
        # Certifique-se de que a categoria está em maiúsculas, já que suas categorias válidas estão em maiúsculas
        categoria_escolhida = categoria_escolhida.upper()
        # Filtrar o DataFrame para incluir apenas as linhas que contêm a categoria escolhida
        df_filtrado = df[
            df["Em quais categorias sua denúncia se encaixa?"]
            .str.upper()
            .str.contains(categoria_escolhida)
        ]
        # Contar denúncias por empresa na categoria escolhida
        contagem_por_empresa = (
            df_filtrado["Nome da empresa"].value_counts(normalize=True) * 100
        )
        # Converter a série em DataFrame para melhor manipulação e visualização
        df_resultado = contagem_por_empresa.reset_index()
        df_resultado.columns = ["Nome da empresa", "Porcentagem de denúncias"]
        # Ordenar o DataFrame pelo número de denúncias em ordem decrescente
        df_resultado = df_resultado.sort_values(
            by="Porcentagem de denúncias", ascending=False
        )
        return df_resultado.head(5)


if categorias:
    for categoria_selecionada in categorias:
        resultado = calcular_porcentagem_denuncias_por_empresa_categoria(
            df, categoria_selecionada
        )

        # Subtítulo para cada categoria
        st.subheader(
            f"Porcentagem de denúncias na categoria '{categoria_selecionada}':"
        )

        # Gerar o gráfico de barras com Altair
        chart = (
            alt.Chart(resultado)
            .mark_bar(color="#031f6d")
            .encode(
                x=alt.X("Nome da empresa:N", sort="-y"),
                y=alt.Y("Porcentagem de denúncias:Q"),
                color=alt.Color("Nome da empresa:N", legend=None),
                tooltip=["Nome da empresa", "Porcentagem de denúncias"],
            )
            .properties(width=600)
        )

        # Exibir o gráfico de barras no Streamlit
        st.altair_chart(chart, use_container_width=True)


if st.session_state.empresa_selecionada:
    # Filter complaints for the selected company and recalculate categories
    df_empresa = df[df["Nome da empresa"].isin(st.session_state.empresa_selecionada)]
    categorias_contagem_empresa = normalize_and_count_categories(
        df_empresa, "Em quais categorias sua denúncia se encaixa?"
    )
    st.subheader(
        f"Categorias de Denúncias (%) - {st.session_state.empresa_selecionada}"
    )
    # Create the chart with the sorted DataFrame
    bar_chart = (
        alt.Chart(categorias_contagem_empresa)
        .mark_bar(color="#031f6d")
        .encode(
            x=alt.X(
                "Em quais categorias sua denúncia se encaixa?:N",
                sort=alt.EncodingSortField(field="Value", op="sum", order="descending"),
            ),
            y=alt.Y("Value:Q", title="Porcentagem (%)"),
        )
    )

    st.altair_chart(bar_chart, use_container_width=True)
    st.subheader(f"Denúncias da Empresa: {st.session_state.empresa_selecionada}")
    st.dataframe(df_empresa[["Denúncia"]], use_container_width=True, hide_index=True)
else:
    # Assegure-se de que esta linha seja executada antes de criar o gráfico inicial
    categorias_contagem = normalize_and_count_categories(
        df, "Em quais categorias sua denúncia se encaixa?"
    )

    # Agora, crie o gráfico de barras com esses dados processados
    st.subheader("Categorias de Denúncias (%)")

    bar_chart = (
        alt.Chart(categorias_contagem)
        .mark_bar(color="#031f6d")
        .encode(
            x=alt.X(
                "Em quais categorias sua denúncia se encaixa?:N",
                title="Categoria",
                sort=alt.SortField(field="Value", order="descending"),
            ),  # Certifique-se de que 'index' é o nome correto para a coluna de categorias
            y=alt.Y("Value:Q", title="Porcentagem (%)"),
        )
    )

    st.altair_chart(bar_chart, use_container_width=True)
