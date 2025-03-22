import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tiers")

df=pd.read_csv("https://raw.githubusercontent.com/coka8991/BlackPapayaItems/main/Items.csv")

st.title("Items Black Papaya")

df["response"] = df["response"].apply(lambda x: "Tier Set" if x == "Tierset" else x)

#cambiamos la columna a tipo fecha
df["date"] = pd.to_datetime(df["date"])

#filtramos por el inicio del parche
df=df[df["date"] >= "2025-03-5"]

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

dfFiltered = df[df["response"].isin(FiltroPorEspeciales)]
dfFiltered.loc[:, "WowHeadURL"] = dfFiltered.apply(
    lambda row: "https://www.wowhead.com/item=" + str(row["itemID"]) + "?bonus=" + ":".join(row["itemString"].split(":")[14:]),
    axis=1
)

dfFiltered.loc[:, "WowHeadURL_Link"] = dfFiltered["WowHeadURL"].apply(lambda url: f"[{url}]({url})")
st.text("Cantidad de tiers por player.")
st.table(df[(df["response"]=="Tier Set") & (pd.isna(df["equipLoc"]))].groupby(["player"]).size().sort_values(ascending=False))