import json
import csv

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px

DEBUG = 0

# load a .csv file from its path
def read_csv_file(path) :
    data = []
    with open(path) as file :
        reader = csv.reader(file, delimiter = ',')
        for row in reader :
            data.append(row)

    data.pop(0)
    return data

# Append .json data into a .csv file
def write_csv_file(path, data) :
    with open(path, "a", newline = "") as file :
        writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_NONNUMERIC)
        for pub in data :
            row = [pub['id'], pub['title'], pub['date'], pub['journal']]
            writer.writerow(row)


# Load a .json file from its path
def read_json_file(path) :
    with open(path, "r") as file :
        data = json.load(file)
    return data

# Correct the id of each medical publication
def correct_pubmed_id(pubmed_json) :
    current_pub_id = pubmed_json[0]['id']
    if isinstance(current_pub_id, str) :
        current_pub_id = int(current_pub_id)

    for pub in pubmed_json :
        pub['id'] = current_pub_id
        current_pub_id = current_pub_id + 1

    return pubmed_json

# Save the corrected medical publication data as a .json file
def write_json_file(path, data) :
    with open(path, "w", newline = "") as file :
        json.dump(data, file)

# -------------------------------------------------------------------------

# Read the date and construct the relashionship graph
# Generate a set of nodes and edges
# Each node represents a drug, a trial, a medical publication or a journal
# Each edge represent a reference from a trial, a medical publication or a journal to a drug
def read_relationships() :

    nodes = []
    edges = []

    current_node_id = 0
    current_edge_id = 0

    for drug in drugs_csv :
        current_drug = drug[1]
        if DEBUG :
            print("\n" +current_drug)

        if create_node(current_node_id, "drug", current_drug, nodes) :
            current_drug_id = current_node_id
            current_node_id = current_node_id + 1

            trials_references = check_references(current_drug, trials_csv, "trial")
            current_node_id, current_edge_id = manage_references(current_drug_id, current_node_id, current_edge_id, trials_references, nodes, edges)

            pubmed_references = check_references(current_drug, pubmed_csv, "pubmed")
            current_node_id, current_edge_id = manage_references(current_drug_id, current_node_id, current_edge_id, pubmed_references, nodes, edges)

    if DEBUG :
        print("\nNodes : ")
        for node in nodes :
            print(node)

        print("\nEdges : ")
        for edge in edges :
            print(edge)

    return nodes, edges

# Get a node id from its parameters
def get_node_id(type, label, nodes) :
    for node in nodes :
        if type in node and label in node :
             return node[0]
    return -1

# Get an edge id from its parameters
def get_edge_id(src, dest, date, edges) :
    for edge in edges :
         if src in edge and dest in edge and date in edge :
             return edge[0]
    return -1

# Generate a node if it does not already exist
def create_node(id, type, label, nodes) :
    if not node_already_exists(type, label, nodes) :
        new_node = (id, type, label)
        nodes.append(new_node)
        if DEBUG :
            print("Created node : (" + str(id) +" " +type + " " +label +")")
        return True
    else :
        if DEBUG :
            print("Node already exists @id :" +str(get_node_id(type, label, nodes)) +" ... (" + str(id) +" " +type + " " +label +")")
        return False

# Generate an edge if it does not already exist
def create_edge(id, src, dest, date, edges) :
    if not edge_already_exists(src, dest, date, edges) :
        new_edge = (id, src, dest, date)
        edges.append(new_edge)
        if DEBUG :
            print("Created edge : (" + str(new_edge[0]) +" " +str(new_edge[1]) + " " +str(new_edge[2]) +" " +new_edge[3] + ")")
        return True
    else :
        if DEBUG :
            print("Edge already exist @id :" +str(get_edge_id(src, dest, date, edges)) +" ... (" +str(id) +" " +str(src) + " " +str(dest) +" " +date + ")")
        return False

# Check if a node already exists
def node_already_exists(type, label, nodes) :

    for node in nodes :
        if node[1] == type and node[2] == label :
            return True
    return False

# Check if an edge already exists
def edge_already_exists(src, dest, date, edges) :

    for edge in edges :
        if edge[1] == src and edge[2] == dest and edge[3] == date :
            return True
    return False

# Find all the trials, medical publications and journals that reference a drug
def check_references(drug_label, data_csv, data_type) :

    references = []

    for trial in data_csv :

        if drug_label.lower() in trial[1].lower() :
            references.append((data_type, trial[1], trial[2]))
            references.append(("journal", trial[3], trial[2]))

    return references

# Construct the relashionship graph of a drug
# From the list of references of the drug, generate the nodes and link them with edges
def manage_references(current_drug_id, current_node_id, current_edge_id, references, nodes, edges) :
    for ref in references :

        if DEBUG :
            print("\n")
            print("Drug_id : " +str(current_drug_id))
            print("Node_id : " +str(current_node_id))
            print("Edge_id : " +str(current_edge_id))
            print(ref)

        if create_node(current_node_id, ref[0], ref[1], nodes) :

            if create_edge(current_edge_id, current_drug_id, current_node_id, ref[2], edges) :
                current_edge_id = current_edge_id + 1

            current_node_id = current_node_id + 1

        else :

            ref_id = get_node_id(ref[0], ref[1], nodes)
            if not ref_id == -1 :
                if create_edge(current_edge_id, current_drug_id, ref_id, ref[2], edges) :
                    current_edge_id = current_edge_id + 1

    return current_node_id, current_edge_id

# Construct the .json data used to graphically generate the graph
def construct_json_data(nodes, edges) :
    elements = []

    for node in nodes :
        element = {}
        node_dict = {}
        node_dict['id'] = str(node[0])
        if not node[1] == "pubmed" and not node[1] == "trial":
            node_dict['label'] = node[2]
        else :
            node_dict['label'] = ""
        node_dict['classes'] = node[1]
        element['data'] = node_dict
        elements.append(element)

    for edge in edges :
        element = {}
        edge_dict = {}
        edge_dict['source'] = str(edge[1])
        edge_dict['target'] = str(edge[2])
        edge_dict['classes'] = "edge"
        edge_dict['label'] = ""
        element['data'] = edge_dict
        elements.append(element)

    layout = {}
    layout['name'] = 'circle'

    style = {}
    style['width'] = '1800px'
    style['height'] = '1100px'

    if DEBUG :
        for element in elements :
            print(element)

    return elements, layout, style

# -------------------------------------------------------------------------

# Compute the journal that refers to the most of drugs
def journal_analytic(graph_data) :

    journals = get_journals(graph_data)
    edges = get_edges(graph_data)

    journals_refs = []

    max_ref = 0
    max_ref_journal = journals[0]

    for journal in journals :
        nb_references = count_references(journal[0], edges)

        if DEBUG :
            print(journal)
            print("References : " +str(nb_references))

        if nb_references > max_ref :
            max_ref = nb_references
            max_ref_journal = journal

    return max_ref_journal, max_ref

# Retrieve the journals data from the .json data used to graphically generate the graph
def get_journals(graph_data) :
    journals = []
    for data in graph_data :
        if data["data"]["classes"] == "journal" :
            journals.append((data["data"]["id"], data["data"]["label"]))
    return journals

# Retrieve the edges data from the .json data used to graphically generate the graph
def get_edges(graph_data) :
    edges = []
    for data in graph_data :
        if data["data"]["classes"] == "edge" :
            edges.append((data["data"]["source"], data["data"]["target"]))
    return edges

# Count the nb of references to drugs of a journal
def count_references(journal_id, edges) :
    cpt = 0
    for edge in edges :
        if journal_id in edge :
            cpt = cpt + 1
    return cpt
# -------------------------------------------------------------------------

# Load and correct the .json source file
pubmed_json = read_json_file("pubmed.json")
pubmed_json = correct_pubmed_id(pubmed_json)

# Write medical publication data from the .json file to the .csv file
write_csv_file("pubmed.csv", pubmed_json)

# Load the different .csv source files
drugs_csv = read_csv_file("drugs.csv")
pubmed_csv = read_csv_file("pubmed.csv")
trials_csv = read_csv_file("clinical_trials.csv")

# -------------------------------------------------------------------------

# Generation nodes and edges from the different .csv file
nodes, edges = read_relationships()
# Construct the .json data used to graphically generate the graph
elements_, layout_, style_ = construct_json_data(nodes, edges)
# Write the .json data into a .json file
write_json_file("graph.json", elements_)

# -------------------------------------------------------------------------

# Read the previously written .json file
references_data = read_json_file("graph.json")
# Compute the journal that refers to the most of drugs and the nb of references
max_ref_journal, max_ref = journal_analytic(references_data)
# Print the result
print(max_ref_journal)
print(max_ref)

# -------------------------------------------------------------------------

# Graphically generate the relashionship graph with DASH

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Drugs references :"),
    cyto.Cytoscape(
        id = 'drugs_refs',
        elements = elements_,
        layout = layout_,
        style = style_,
    )
])

app.run_server(debug = True)
