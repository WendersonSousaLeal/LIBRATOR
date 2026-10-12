import pandas as pd

# 1. Carrega o novo banco de dados
df = pd.read_csv('banco_dados_libras.csv', header=None)

# Renomeia a primeira coluna para facilitar a manipulação
df = df.rename(columns={df.columns[0]: 'label'})

# 2. Filtra removendo os números (dígitos) e o rótulo 'AB' (ou outros indesejados)
# Mantém apenas linhas cujos rótulos NÃO são dígitos e são diferentes de 'AB'
df_filtrado = df[~df['label'].astype(str).str.isdigit() & (df['label'] != 'AB')]

# (Opcional) Se quiser remover também 'ESPACO' e 'APAGAR', caso queira apenas o alfabeto de A a Z:
# df_filtrado = df_filtrado[~df_filtrado['label'].isin(['ESPACO', 'APAGAR'])]

# 3. Salva o resultado no novo arquivo
df_filtrado.to_csv('landmarks_dataset_2.csv', index=False, header=False)

print("Dataset filtrado e salvo como 'landmarks_dataset_2.csv' com sucesso!")
print("Rótulos restantes:", df_filtrado['label'].unique())