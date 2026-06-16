import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

st.set_page_config(page_title="AUiX Stakeholder Map", layout="wide")

organizations = [
    {"name": "AUiX", "type": "Hub", "engagement": None, "cadence": None, "expertise": []},
    {"name": "AWC", "type": "Air University", "engagement": 10, "cadence": "monthly", "expertise": []},
    {"name": "ACSC", "type": "Air University", "engagement": 25, "cadence": "biweekly", "expertise": ["AI", "VR", "PME", "War Game"]},
    {"name": "SOS", "type": "Air University", "engagement": 40, "cadence": "weekly", "expertise": ["VR", "PME", "War Game"]},
    {"name": "Lemay", "type": "Air University", "engagement": 10, "cadence": "monthly", "expertise": ["VR", "3D Printing", "War Game"]},
    {"name": "HII", "type": "Industry", "engagement": 24, "cadence": "biweekly", "expertise": []},
    {"name": "OMNI Federal", "type": "Industry", "engagement": 10, "cadence": "monthly", "expertise": []},
    {"name": "Auburn", "type": "Academia", "engagement": 10, "cadence": "monthly", "expertise": ["AI", "VR", "3D Printing"]},
    {"name": "AUM", "type": "Academia", "engagement": 50, "cadence": "weekly", "expertise": ["AI", "VR", "3D Printing"]},
    {"name": "Stanford", "type": "Academia", "engagement": 30, "cadence": "weekly", "expertise": ["AI", "VR", "War Game"]},
    {"name": "BESPIN", "type": "Mil & Gov", "engagement": 12, "cadence": "monthly", "expertise": ["PME"]},
    {"name": "Pathfinder", "type": "Mil & Gov", "engagement": 4, "cadence": "quarterly", "expertise": ["PME"]},
    {"name": "SBIR Advisor", "type": "Industry", "engagement": 12, "cadence": "monthly", "expertise": ["PME"]},
]

partners = [
    ("AUiX", "AWC"),
    ("AUiX", "ACSC"),
    ("AUiX", "SOS"),
    ("AUiX", "Lemay"),
    ("AUiX", "HII"),
    ("AUiX", "OMNI Federal"),
    ("AUiX", "Auburn"),
    ("AUiX", "AUM"),
    ("AUiX", "Stanford"),
    ("AUiX", "BESPIN"),
    ("AUiX", "Pathfinder"),
    ("AUiX", "SBIR Advisor"),
]

df = pd.DataFrame(organizations)

st.title("AUiX Stakeholder Map")
st.write("Explore organizations, expertise areas, engagement cadence, and stakeholder relationships.")

st.sidebar.header("Filters")

search = st.sidebar.text_input("Search organization")

type_options = sorted(df["type"].dropna().unique())
selected_types = st.sidebar.multiselect("Organization Type", type_options)

all_expertise = sorted({item for sublist in df["expertise"] for item in sublist})
selected_expertise = st.sidebar.multiselect("Expertise", all_expertise)

filtered = df.copy()

if search:
    filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]

if selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]

if selected_expertise:
    filtered = filtered[
        filtered["expertise"].apply(lambda items: any(x in items for x in selected_expertise))
    ]

col1, col2, col3 = st.columns(3)
col1.metric("Organizations", len(df))
col2.metric("Partnerships", len(partners))
col3.metric("Expertise Areas", len(all_expertise))

st.subheader("Organization Profile")

selected_org = st.selectbox(
    "Choose an organization",
    sorted(df["name"].tolist())
)

org = df[df["name"] == selected_org].iloc[0]

profile_col1, profile_col2 = st.columns(2)

with profile_col1:
    st.markdown(f"### {org['name']}")
    st.write(f"**Type:** {org['type']}")
    st.write(f"**Engagements Last Year:** {org['engagement'] if pd.notna(org['engagement']) else 'N/A'}")
    st.write(f"**Cadence:** {org['cadence'] if pd.notna(org['cadence']) else 'N/A'}")

with profile_col2:
    st.write("**Expertise:**")
    if org["expertise"]:
        for item in org["expertise"]:
            st.write(f"- {item}")
    else:
        st.write("N/A")

    connected = []
    for a, b in partners:
        if a == selected_org:
            connected.append(b)
        elif b == selected_org:
            connected.append(a)

    st.write("**Connected Organizations:**")
    if connected:
        for item in connected:
            st.write(f"- {item}")
    else:
        st.write("N/A")

st.subheader("Interactive Network Map")

visible_orgs = set(filtered["name"].tolist())
visible_orgs.add("AUiX")

net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="black")

for _, row in df.iterrows():
    name = row["name"]

    if name not in visible_orgs:
        continue

    label = name
    title = f"""
    Organization: {row['name']}
    Type: {row['type']}
    Engagements Last Year: {row['engagement']}
    Cadence: {row['cadence']}
    Expertise: {', '.join(row['expertise']) if row['expertise'] else 'N/A'}
    """

    size = 30 if name == "AUiX" else 18

    net.add_node(
        name,
        label=label,
        title=title,
        size=size
    )

for source, target in partners:
    if source in visible_orgs and target in visible_orgs:
        net.add_edge(source, target, title="PARTNER_WITH")

net.toggle_physics(True)
net.show_buttons(filter_=["physics"])

with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
    net.save_graph(tmp_file.name)
    html = open(tmp_file.name, "r", encoding="utf-8").read()

components.html(html, height=700, scrolling=True)

st.subheader("Organization Directory")

display_df = filtered.copy()
display_df["expertise"] = display_df["expertise"].apply(lambda x: ", ".join(x) if x else "N/A")
display_df = display_df.rename(columns={
    "name": "Organization",
    "type": "Type",
    "engagement": "Engagements Last Year",
    "cadence": "Cadence",
    "expertise": "Expertise"
})

st.dataframe(display_df, use_container_width=True)