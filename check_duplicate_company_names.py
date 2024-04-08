import pandas as pd

# Carregar o arquivo CSV
df = pd.read_csv("stream.csv", usecols=["Em quais categorias sua denúncia se encaixa?"])


# Função para processar as categorias de denúncias
def processar_categorias(texto):
    categorias = texto.split(";") if pd.notnull(texto) else []
    return [categoria.strip() for categoria in categorias]


# Aplicar a função em cada linha e expandir o resultado em uma lista
lista_de_categorias = (
    df["Em quais categorias sua denúncia se encaixa?"]
    .apply(processar_categorias)
    .explode()
)

# Salvar o resultado em um novo arquivo CSV
lista_de_categorias.to_csv("categorias_de_denuncias.csv", index=False, header=False)

print("Arquivo 'categorias_de_denuncias.csv' criado com sucesso.")
