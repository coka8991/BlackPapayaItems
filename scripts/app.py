import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Items Black Papaya",layout="wide")
df=pd.read_csv("https://raw.githubusercontent.com/coka8991/BlackPapayaItems/main/Items.csv")

st.title("Items Black Papaya")

df["response"] = df["response"].apply(lambda x: "Tier Set" if x == "Tierset" else x)

#cambiamos la columna a tipo fecha
df["date"] = pd.to_datetime(df["date"])

#filtramos por el inicio del parche
df=df[df["date"] >= "2025-08-13"]

#los boes tienen esta caracteristica por eso los quitamos
df=df[df["votes"]!="nil"]
df["note"]=df["note"].fillna("")

#quitamos los patterns
df = df[~df["item"].str.contains("Pattern:")]
df = df[~df["item"].str.contains("Design: ")]
df = df[~df["item"].str.contains("Recipe:")]
df = df[~df["item"].str.contains("Plans:")]

#Medimos las estadisticas de este tipo de items
FiltroPorEspeciales = ["Tier Set", "Bis", "Pre-Bis"]
FiltroPorEspeciales = st.multiselect(
    "Selecciona filtros:", 
    ["Tier Set", "Bis", "Pre-Bis", "Mejora"], 
    default=["Tier Set", "Bis", "Pre-Bis"]
)
FiltroPorDif = st.multiselect("Selecciona Dificultades",
        ["Normal","Heroic","Mythic"],
        default=["Normal","Heroic","Mythic"])
FiltroPorDif=["Liberation of Undermine-"+i for i in FiltroPorDif]

dfFiltered = df[df["response"].isin(FiltroPorEspeciales)]
dfFiltered = dfFiltered[dfFiltered["instance"].isin(FiltroPorDif)]
#dfFiltered.loc[:, "WowHeadURL"] = dfFiltered.apply(
#    lambda row: "https://www.wowhead.com/item=" + str(row["itemID"]) + "?bonus=" + ":".join(row["itemString"].split(":")[14:]),
#    axis=1
#)

#dfFiltered.loc[:, "WowHeadURL_Link"] = dfFiltered["WowHeadURL"].apply(lambda url: f"[{url}]({url})")

# Crear un DataFrame que cuente cuántas veces aparece cada valor en FiltroPorEspeciales para cada jugador
ItemsEspeciales = dfFiltered.pivot_table(
    index="player",
    columns="response",
    aggfunc="size",
    fill_value=0
).reset_index()


# Añadir una columna con el total de eventos sumando las tres categorías
ItemsEspeciales["Total"]=0
for i in FiltroPorEspeciales:
    ItemsEspeciales["Total"] += ItemsEspeciales[i] 

# Ordenar por la columna 'event_count' de mayor a menor

#st.markdown(ItemsEspeciales.sort_values(by="Total", ascending=False).to_markdown(index=False))

df_aux=ItemsEspeciales.sort_values(by="Total", ascending=True)
fig, ax = plt.subplots(figsize=(10, 8))
bar_width = 0.7  # Ancho de las barras
colores = {
        "Bis": "darkorange",
        "Pre-Bis": "purple",
        "Tier Set": "steelblue",
        "Mejora": "seagreen"
    }
base = pd.Series([0] * len(df_aux), index=df_aux.index)

# Apilar las barras
for columna in FiltroPorEspeciales:
        ax.barh(df_aux["player"], df_aux[columna], left=base, color=colores[columna], label=columna)
        base += df_aux[columna] 

# Etiquetas y título
ax.set_xlabel("Items")
ax.set_ylabel("Jugador")
ax.set_title("Distribución de items por Jugador")
ax.legend()
col1, col2 =st.columns(2)
with col1:
     st.table(ItemsEspeciales.sort_values(by="Total", ascending=False))
with col2:
    st.pyplot(fig,)

options = st.selectbox("Selecciona Un player para ver los items",ItemsEspeciales["player"].unique(),index=None)
if options!=None:
    result = dfFiltered[dfFiltered["player"] == options][["item","equipLoc", "response", "date", "votes", "instance", "note"]]
    st.markdown(result.to_markdown())



