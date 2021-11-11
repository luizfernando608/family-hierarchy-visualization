import pandas as pd

import streamlit as st

import networkx as nx

import matplotlib.colors as mcolors


import dash_html_components as html
import dash_cytoscape as cyto

#Coletando Data Frame do xls
df = pd.read_excel('Static-visuzalization-test/familia.xls')
df.head()

## number of classes
len(df['pai-mae'].unique())

#possible colors' names
mcolors.cnames.keys()

# Contando o número de pessoas no banco de dados
linhas = len(df['pai-mae'].unique())
# Criando uma lista de cores disponíveis
chosen = list(mcolors.cnames.keys())
# Criando uma lista de cores de acordo com o número de pessoas
chosen = chosen[1:linhas+1]
# Dicionário das pessoas correspondentes a cada cor
colors = dict(zip(df['pai-mae'].unique(),chosen))
print(colors)
# Criando um dataframe com as pessoas e suas cores correspondentes.
df_colors = pd.DataFrame({'classes':df['pai-mae'].unique(), 'colors':chosen})
df_colors.head()

#Criando entidade do Grafo
G = nx.DiGraph()
# Adicionando Nós
# Nessa etapa são adicionados os nós soltos com valores e cores
for idx in df.index:  
   G.add_node(
      df.loc[idx, 'filho'],
         label=df.loc[idx, 'filho'], 
         color=colors[df.loc[idx,'pai-mae']],
         className=df.loc[idx, 'filho']
      )
   
# Nessa etapa, são estabelecidas as conexões entre os grafos
G.add_edges_from(zip(df['filho'].values, df['pai-mae'].values),
                 color='turquoise', 
                 relation = 'filho de')


for g in G.nodes():
   G.edges(data=True)

cyto_family_nodes = nx.readwrite.json_graph.cytoscape_data(G)['elements']['nodes']
cyto_family_edges = nx.readwrite.json_graph.cytoscape_data(G)['elements']['edges']


stylesheet=[
            {'selector': 'node', 
                'style': { 'label': 'data(label)'}, 
                "text-wrap": "wrap"},
            
            "layout":{
                'name':'breadthfirst',
                'roots': '#Nonato'
            }
        ]

from streamlit_cytoscapejs import st_cytoscapejs

st_cytoscapejs(cyto_family_edges+cyto_family_nodes, stylesheet)





# app.run_server(debug=False)

# st.plotly_chart(app)