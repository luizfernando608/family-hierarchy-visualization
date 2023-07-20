
#%%
import pandas as pd
import networkx as nx
import dash
import dash_html_components as html
import dash_cytoscape as cyto
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from networkx.algorithms.traversal.depth_first_search import dfs_tree
import numpy as np
import sqlalchemy as sql
import os
#%%

root_path = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(root_path,"Data","family.db")

engine = sql.create_engine(f'sqlite:///{database_path}')

query_names = "select *  from names"
query_relations = "select * from relations"

with engine.connect() as conn:
    tuple_names = conn.execute(query_names).fetchall()
    tuple_relations = conn.execute(query_relations).fetchall()

names_data = pd.DataFrame(tuple_names, columns=["id", "nome","apelido"])
#%%
relations_data = pd.DataFrame(tuple_relations,columns=["id","pai_id","mae_id"])
#%%
name_by_id = names_data[["id","nome"]].set_index("id").to_dict()["nome"]

#%%
# Criando o Grafo
family_tree = nx.DiGraph()
# Adicionando os nodes
for row in names_data.values:
    short_name = row[1].split(" ")[0]+" "+row[1].split(" ")[-1]
    family_tree.add_node(str(row[0]),
                        id=str(row[0]),
                        short_name=short_name,
                        full_name = row[1])

#%%
edges_list = []
count = 0
for relation in relations_data.values:
    count += 1
    if not np.isnan(relation[1]):
        edges_list.append((str(int(relation[0])),str(int(relation[1]))))
    if not np.isnan(relation[2]):
        edges_list.append((str(int(relation[0])),str(int(relation[2]))))

family_tree.add_edges_from(edges_list)

#%%
family_degrees = family_tree.in_degree
max_degre = max([degree for id, degree in family_degrees])
green = np.array((57, 173, 51))
brown = np.array((51, 31, 15))
step = (brown-green)/max_degre

for id, node in family_tree.nodes(data=True):
    degree = family_degrees[node['id']]
    node["size"] = ((degree)+5)*5
    node["color"] = f"rgb{str(tuple(green+step*degree))}"

#%%
cyto_family_nodes = nx.readwrite.json_graph.cytoscape_data(family_tree)['elements']['nodes']
cyto_family_edges = nx.readwrite.json_graph.cytoscape_data(family_tree)['elements']['edges']


#%%
def get_path(family_tree: nx.classes.digraph.DiGraph, source_id: str, target_id: str):
    source = nx.descendants(family_tree, source_id)
    source.add(source_id)
    target = nx.descendants(family_tree, target_id)
    target.add(target_id)
    intersec_parent_nodes = target.intersection(source)
    shortest_path_length = float("inf")
    all_shortest_paths = []
    for parent in intersec_parent_nodes:
        path_length = nx.shortest_path_length(
            family_tree, source_id, parent)+nx.shortest_path_length(family_tree, target_id, parent)
        if path_length < shortest_path_length:
            all_shortest_paths.clear()

        if path_length <= shortest_path_length:
            source_to_parent = [path for paths in nx.all_shortest_paths(
                family_tree, source_id, parent) for path in paths]
            target_to_parent = [path for paths in nx.all_shortest_paths(
                family_tree, target_id, parent) for path in reversed(paths[:-1])]
            all_shortest_paths.append(source_to_parent+target_to_parent)
            shortest_path_length = path_length

    return all_shortest_paths


def dict_to_highlight_path(paths: list):
    edge_style = []
    node_style = []
    for node_path in paths:
        for idx in node_path[1:-1]:
            node_style += [{"selector": f"#{idx}",
                           "style": {"background-color": "blue"}}]

        node_style += [{"selector": f"#{node_path[0]}",
                       "style": {"background-color": "red"}}]
        node_style += [{"selector": f"#{node_path[-1]}",
                       "style": {"background-color": "red"}}]

        for num, idx in enumerate(node_path[:-1]):
            edge_style += [
                {'selector': f"[target = '{node_path[num]}' ][source = '{node_path[num+1]}']",
                 'style': {
                     'line-color': "blue",
                     'z-index': "10",
                     "width": "10px",
                     "opacity": "0.7"
                 }},
                {'selector': f"[source = '{node_path[num]}' ][target = '{node_path[num+1]}']",
                 'style': {
                     'line-color': "blue",
                     'z-index': "10",
                     "width": "10px",
                     "opacity": "0.7"
                 }},
            ]

    return node_style + edge_style
#%%
cyto.load_extra_layouts()
#%%
cytoscape_stylesheet = [
    {'selector': 'node',
     'style': {'label': 'data(short_name)',
               'padding': 'data(size)',
               'border-width': '1px',
               'border-style': 'solid',
               'border-color': "black",
               "background-color": "data(color)",
               "font-family":"Verdana",
               "font-weight": "600",
               "z-index":"15",
               "text-transform":"uppercase",
               "text-wrap":"wrap",
               "text-max-width":"10",

               "text-halign":"center",
               "text-valign":"center",
            #    "text-border-opacity":"1",
            #    "text-border-width":"10",
            #    "text-border-color":"white",

            #    "text-background-color":"white",
            #    "text-background-opacity":"1",
               "color":"white",
               "text-outline-color":"black",
               "text-outline-opacity":"1",
               "text-outline-width":"1"
            #    "text-overflow-wrap":"whitespace"
               },
     },
    {'selector': 'edge',
     'style': {
         'line-color': "rgb(51, 31, 15)",
         'opacity': '0.5',
         "width": "5px"
     }},
]
app = dash.Dash("Family Network")
server = app.server

app.layout = html.Div(id="body", children=[
    html.Article([
        html.Details([
        html.Summary("Menu"),
        html.Div(id="box-fields", children=[
            html.Div(id="header", children=[
                html.H1('Surubeju  Network', id="title"),
                html.Img(id="image", src='/assets/tree.png')
            ]),
            html.Div(id="box-people-connection", children=[
                html.H2("Parentesco entre duas pessoas:"),
                html.Div([
                    dcc.Dropdown(
                        id='input-source-id',
                        options=[{'label': name.split(" ")[0]+" "+name.split(" ")[-1], 'value': idx}
                                 for (idx, name) in name_by_id.items()],
                        searchable=True,
                        className="dropdown",
                        placeholder="Selecione pessoa 1"
                    ),
                    dcc.Dropdown(
                        id='input-target-id',
                        options=[{'label': name.split(" ")[0]+" "+name.split(" ")[-1], 'value': idx}
                                 for (idx, name) in name_by_id.items()],
                        searchable=True,
                        className="dropdown",
                        placeholder="Selecione pessoa 2"
                    ),
                ],
                    className="column2"),
                html.P(id="warning", style={"color": "red"}),
                html.P(id="path-length")
            ]),
            html.Div(id="box-ancestors", children=[
                html.H2("Conheça a árvore de alguém:"),
                html.Div(children=[
                    dcc.Dropdown(id='ancestors-descendants',
                                 className="dropdown",
                                 options=[{'label': "Ancestrais", 'value': True},
                                        {'label': "Descendentes", 'value': False}],
                                 searchable=False,
                                 placeholder="Ancestrais ou Descendentes?"),
                    dcc.Dropdown(id='input-all',
                                 className="dropdown",
                                 options=[{'label': name.split(" ")[0]+" "+name.split(" ")[-1], 
                                          'value': idx}
                                          for (idx, name) in name_by_id.items()],
                                 searchable=True,
                                 placeholder="Selecione uma pessoa"),
                                 ], className="column2",)
            ]),
        ])]),
        cyto.Cytoscape(
            id='cytoscape',
            elements=cyto_family_nodes+cyto_family_edges,
            layout={'name': 'cose-bilkent'},
            style={'width': '100vw', 'height': '100vh'},
            stylesheet=cytoscape_stylesheet)
    ]),
    # dcc.Interval(
    #     id="interval_component",
    #     interval=5*1000,
    #     n_intervals=0
    # ),
    html.P(id="interval_result"),
])

# @app.callback([Output('input-source-id','options'),
#             Output('input-target-id','options'),
#             Output('input-all','options')],
#             Input('interval_component','n_intervals'))


@app.callback(Output('cytoscape', 'elements'),
             Output('cytoscape', 'layout'),
             Input('input-all', 'value'), 
             Input('ancestors-descendants', 'value'))
def get_all_descendants(source_id, is_ancestors):
    subtree_elements_nodes = []
    subtree_elements_edges = []
    if source_id is not None and is_ancestors is not None:
        if not is_ancestors:
            reverse_family_tree = family_tree.reverse(copy=True)
        else:
            reverse_family_tree = family_tree
        sub_tree = dfs_tree(reverse_family_tree, str(source_id))

        for id_node, data in sub_tree.nodes(data=True):
            temp_dict = {'data': reverse_family_tree.nodes(data=True)[id_node]}
            temp_dict["data"]["value"] = id_node
            temp_dict["data"]["name"] = id_node
            subtree_elements_nodes.append(temp_dict)

        subtree_elements_edges = nx.readwrite.json_graph.cytoscape_data(sub_tree)['elements']['edges']
        # print(subtree_elements_nodes)
        return subtree_elements_edges + subtree_elements_nodes,{'name': 'dagre'}

    return cyto_family_edges+cyto_family_nodes,{'name': 'cose-bilkent'}


@app.callback(Output('cytoscape', 'stylesheet'),
              Output("warning", "children"),
              Output("path-length","children"),
              Input('input-source-id', 'value'),
              Input('input-target-id', 'value'))
def highlight_node_path(source_id, target_id):
    style = []
    if source_id is not None and target_id is not None:
        path = get_path(family_tree, str(source_id), str(target_id))
        if len(path) == 0:
            return cytoscape_stylesheet+style, "Não há relação entre eles",""
        style = dict_to_highlight_path(path)
        return cytoscape_stylesheet + style,"", f"Relação de {len(path[0])-1}º grau"
    return cytoscape_stylesheet + style,"",""


app.run_server(debug=False, port=8060)