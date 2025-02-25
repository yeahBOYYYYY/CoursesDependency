import pickle
from tokenize import group

import networkx as nx
from pyvis.network import Network
from IPython.display import display, HTML


def create_dependency_graph(course_data: dict):
    # Create an interactive visualization
    net = Network(
        height="749px",
        width="100%",
        directed=True,
        notebook=False,
        neighborhood_highlight=True,
        select_menu=True,
        filter_menu=True,
        bgcolor="white",
        cdn_resources="remote"
    )

    for course, prerequisites in course_data.items():
        faculty = prerequisites[0]
        net.add_node(course, label=course, group=faculty)

    for course, prerequisites in course_data.items():
        prerequisites = prerequisites[1::]
        for prereq in prerequisites:
            try:
                net.add_edge(prereq, course)
            except:
                net.add_node(prereq, label=prereq, group="לא קיים")
                net.add_edge(prereq, course)


    # Save and show the graph
    html = net.generate_html()
    with open("example.html", mode='w', encoding='utf-8') as fp:
            fp.write(html)
    display(HTML(html))


if __name__ == "__main__":

    with open("prerequisites.pkl", "rb") as file:
        dependency_data = pickle.load(file)

    create_dependency_graph(dependency_data)
