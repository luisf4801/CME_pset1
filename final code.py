# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 14:04:21 2026

@author: Luis
"""
#codigo feito por mim e organizado e comentado com ajuda de AI
import sys
print(sys.version)

import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from stargazer.stargazer import Stargazer
# Pega a pasta onde o script está salvo automaticamente
base_path = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(base_path)


input_path = os.path.join(base_path, "data", "Mega-Sena.xlsx")
export_path = os.path.join(base_path, "output")
# Configuração de diretório e carga de dados
df = pd.read_excel("Raw/Mega-Sena.xlsx")

# --- 1. PRÉ-PROCESSAMENTO E LIMPEZA ---

# Alinhamento: A estimativa do prêmio refere-se ao sorteio seguinte
df['Estimativa prêmio'] = df['Estimativa prêmio'].shift(1)
df = df.dropna(subset=['Estimativa prêmio'])

# Filtro Temporal: Exclusão de sorteios antigos (estimativas zeradas ou inconsistentes)
df['Data do Sorteio'] = pd.to_datetime(df['Data do Sorteio'])
df = df[df["Data do Sorteio"] > '2009-06-01'].reset_index(drop=True)

# Tratamento de Colunas Monetárias (Limpeza de strings e conversão para Float)
colunas_moeda = [
    'Rateio 6 acertos', 'Rateio 5 acertos', 'Rateio 4 acertos', 
    'Acumulado 6 acertos', 'Arrecadação Total', 'Estimativa prêmio',
    'Acumulado Sorteio Especial Mega da Virada'
]


is_dez_31 = (df['Data do Sorteio'].dt.month == 12) & (df['Data do Sorteio'].dt.day == 31)
is_jan_01 = (df['Data do Sorteio'].dt.month == 1) & (df['Data do Sorteio'].dt.day == 1) &(df['Data do Sorteio'].dt.year == 2026)

# Atribuindo 1 se qualquer uma das condições for verdadeira
df['mega_da_virada'] = (is_dez_31 | is_jan_01).astype(int)

for col in colunas_moeda:
    df[col] = (df[col]
               .astype(str)
               .str.replace(r'R\$\s?', '', regex=True)
               .str.replace('.', '', regex=False)
               .str.replace(',', '.', regex=False))
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- 2. MAPEAMENTO DE PREÇOS HISTÓRICOS ---
#dados coletados do site https://graficos.poder360.com.br/PEXGE/1/

def get_ticket_price(data):
    """Retorna o preço da aposta mínima com base na data de vigência."""
    if data >= pd.to_datetime('2025-07-09'): return 6.00
    if data >= pd.to_datetime('2023-05-03'): return 5.00
    if data >= pd.to_datetime('2019-11-10'): return 4.50
    if data >= pd.to_datetime('2015-05-24'): return 3.50
    if data >= pd.to_datetime('2014-05-10'): return 2.50
    return 2.00

df['Preço Aposta'] = df['Data do Sorteio'].apply(get_ticket_price)

# --- 3. ANÁLISES DO PSET ---

### A) Elasticidade via Regressão Log-Log
# O coeficiente de log(X) em uma regressão log(y) representa a elasticidade-preço/renda
y_elasticidade = np.log(df['Arrecadação Total'])
X_elasticidade = sm.add_constant(np.log(df['Estimativa prêmio']))

modelo_a = sm.OLS(y_elasticidade, X_elasticidade).fit()
print("--- Resultado Item A (Elasticidade) ---")
print(modelo_a.summary())

### B) Estimativa do Volume de Jogos
# Proxy para número de jogadores: Total arrecadado / Preço unitário da aposta

# Checagem para garantir que não vamos dividir por zero
if (df['Preço Aposta'] == 0).any():
    raise ValueError("Erro: A coluna contém valores zero. Interrompendo a execução.")

print("O código continua apenas se não houver zeros.")

df["Num. jogos"] = df['Arrecadação Total'] / df['Preço Aposta']

### C) Cálculo do Valor Esperado (VE)
# VE = Σ (Probabilidade de Ganhar * Prêmio) 
# Aqui usamos (Ganhadores / Total de Jogos) como proxy para a probabilidade
df["valor esperado"] = (
    (df['Ganhadores 6 acertos'] / df["Num. jogos"] * df['Rateio 6 acertos']) +
    (df['Ganhadores 5 acertos'] / df["Num. jogos"] * df['Rateio 5 acertos']) +
    (df['Ganhadores 4 acertos'] / df["Num. jogos"] * df['Rateio 4 acertos'])
)

### D) Cálculo do Retorno Líquido
# Retorno = (Valor Esperado / Custo) - 1
df["retorno"] = (df["valor esperado"] / df['Preço Aposta'])

### E) Regressão linear: Prêmio vs. Retorno
X_retorno = df[['Estimativa prêmio']].copy()
X_retorno=X_retorno/1000000
# X_retorno['Estimativa_Quadrado'] = X_retorno['Estimativa prêmio'] ** 2 # Opcional: Ativar para efeito quadrático
X_retorno = sm.add_constant(X_retorno)

modelo_e = sm.OLS(df['retorno'], X_retorno).fit()
print("\n--- Resultado Item E (Modelo Polinomial) ---")
print(modelo_e.summary())

# --- 4. VISUALIZAÇÃO DOS RESULTADOS ---

plt.figure(figsize=(10, 6))

# Dados Reais
sns.scatterplot(data=df, x='Estimativa prêmio', y='retorno', alpha=0.5, label='Dados Reais', color='blue')

# Linha de Tendência (Previsão do Modelo)
x_range = np.linspace(df['Estimativa prêmio'].min(), df['Estimativa prêmio'].max(), 100)
# Cálculo manual da linha baseado nos coeficientes beta_0 e beta_1
y_curva = modelo_e.params[0] + modelo_e.params[1] * x_range/1000000 

plt.plot(x_range, y_curva, color='red', linewidth=3, label='Linha de Tendência (Modelo)')

plt.xlabel('Estimativa do Prêmio (R$)')
plt.ylabel('Retorno Esperado')
plt.title('Relação entre Estimativa de Prêmio e Retorno da Aposta')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()


#metodo não paramétrico

#só como experimento, criei esse modelo de randon forest, usei AI para montar a 
#estrutura mas eu que decidi os parametros e variaveis a serem usadas 

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Preparação dos Dados (Features e Target)

X = df[['Estimativa prêmio', 'mega_da_virada']]
y = df['retorno']

# 2. Split 70% Treino / 30% Teste
# random_state garante que o resultado seja reproduzível
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42
)

# 3. Construção do Modelo
# n_estimators: Número de árvores (100-200 costuma ser um bom equilíbrio)
# max_depth: Limitamos a profundidade para evitar Overfitting (decorar o treino)
rf_model = RandomForestRegressor(
    n_estimators=100, 
    max_depth=7,            # Aumentei um pouco a profundidade já que a folha é restrita
    min_samples_leaf=5,     # <--- O seu pedido aqui
    random_state=42,
    n_jobs=-1
)

# 4. Treino
rf_model.fit(X_train, y_train)

# 5. Previsão fora da amostra (Test Set)
y_pred = rf_model.predict(X_test)

# --- 6. AVALIAÇÃO DE PERFORMANCE ---

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("--- Performance do Random Forest (Fora da Amostra) ---")
print(f"MAE (Erro Médio Absoluto): {mae:.4f}")
print(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.4f}")
print(f"R² Score: {r2:.4f}")

# Exibir importância das variáveis
importancia = pd.Series(rf_model.feature_importances_, index=X.columns)
print("\nImportância das variáveis:")
print(importancia)



import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Criar um conjunto de dados sintético para gerar uma curva suave de previsão
# Vamos variar o prêmio do mínimo ao máximo observado
premios_simulados = np.linspace(df['Estimativa prêmio'].min(), df['Estimativa prêmio'].max(), 500)

# Criar dois cenários: Um para sorteio comum (0) e outro para Mega da Virada (1)
df_comum = pd.DataFrame({'Estimativa prêmio': premios_simulados, 'mega_da_virada': 0})
df_virada = pd.DataFrame({'Estimativa prêmio': premios_simulados, 'mega_da_virada': 1})

# 2. Gerar as previsões do modelo treinado para ambos os cenários
pred_comum = rf_model.predict(df_comum)
pred_virada = rf_model.predict(df_virada)

# 3. Plotagem
plt.figure(figsize=(12, 7))

# Pontos reais do dataset para contexto
sns.scatterplot(data=df, x='Estimativa prêmio', y='retorno', hue='mega_da_virada', 
                palette={0: 'blue', 1: 'gold'}, alpha=0.4, s=60)

# Linhas de previsão do Random Forest
plt.plot(premios_simulados, pred_comum, color='navy', linewidth=2.5, label='Previsão: Sorteio Comum')
plt.plot(premios_simulados, pred_virada, color='darkorange', linewidth=2.5, label='Previsão: Mega da Virada')

# Estética
plt.title('Previsão de Retorno: Prêmio Estimado vs. Tipo de Sorteio', fontsize=14)
plt.xlabel('Estimativa do Prêmio (R$)', fontsize=12)
plt.ylabel('Retorno Esperado', fontsize=12)
plt.legend(title='Legenda')
plt.grid(True, linestyle='--', alpha=0.5)

# Formatar eixo X para milhões/bilhões se necessário
plt.ticklabel_format(style='plain', axis='x') 

plt.show()



#exportando

# --- 4. EXPORTAÇÃO INDIVIDUAL COM STARGAZER (HTML) ---
export_path="output"
# Modelo A: Elasticidade (Log-Log)
st_a = Stargazer([modelo_a])
st_a.title('Análise de Elasticidade - Modelo Log-Log')
st_a.custom_columns(['Elasticidade'], [1])
st_a.rename_covariates({'const': 'Constante', 'x1': 'log(Estimativa prêmio)'}) # Ajuste conforme o nome das suas vars

with open(os.path.join(export_path, "elasticidade_loglog.html"), "w", encoding="utf-8") as f:
    f.write(st_a.render_html())

# Modelo E: Retorno Linear
st_e = Stargazer([modelo_e])
st_e.title('Análise de Retorno - Modelo Linear')
st_e.custom_columns(['Retorno Esperado'], [1])
st_e.rename_covariates({'const': 'Constante', 'Estimativa prêmio': 'Prêmio Estimado (milhões de R$)'})

with open(os.path.join(export_path, "retorno_linear.html"), "w", encoding="utf-8") as f:
    f.write(st_e.render_html())

print(f"Sucesso! Exportados separadamente para {export_path}:")
print("- elasticidade_loglog.html")
print("- retorno_linear.html")
    
# --- 5. VISUALIZAÇÃO E SALVAMENTO DOS GRÁFICOS ---

# Gráfico 1: Linear
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Estimativa prêmio', y='retorno', alpha=0.5, color='blue')
x_range = np.linspace(df['Estimativa prêmio'].min(), df['Estimativa prêmio'].max(), 100)
plt.plot(x_range, modelo_e.params[0] + modelo_e.params[1] * x_range/1000000, color='red', label='Tendência Linear')
plt.title('Regressão Linear: Prêmio vs Retorno')

plt.savefig(os.path.join("output", "plot_linear.png"), dpi=300)
plt.close()

# Gráfico 2: Random Forest
plt.figure(figsize=(12, 7))
premios_sim = np.linspace(df['Estimativa prêmio'].min(), df['Estimativa prêmio'].max(), 500)
pred_comum = rf_model.predict(pd.DataFrame({'Estimativa prêmio': premios_sim, 'mega_da_virada': 0}))
pred_virada = rf_model.predict(pd.DataFrame({'Estimativa prêmio': premios_sim, 'mega_da_virada': 1}))

sns.scatterplot(data=df, x='Estimativa prêmio', y='retorno', hue='mega_da_virada', palette={0: 'blue', 1: 'gold'}, alpha=0.4)
plt.plot(premios_sim, pred_comum, color='navy', linewidth=2, label='RF: Sorteio Comum')
plt.plot(premios_sim, pred_virada, color='darkorange', linewidth=2, label='RF: Mega da Virada')
plt.axhline(y=1, color='red', linestyle='--', label='Referência (E=1)')
plt.title('Random Forest: Impacto do Prêmio e Tipo de Sorteio')
plt.ticklabel_format(style='plain', axis='x')
plt.legend()
plt.savefig(os.path.join("output", "plot_random_forest.png"), dpi=300)

plt.show()