from io import StringIO
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import spacy


nlp = spacy.load("fr_core_news_sm")


nlp = spacy.load("fr_core_news_sm")
def analysefunc(content):
    #lire les données
    data = pd.read_csv(StringIO(content))

    #Crée Dataframe avec que la colonne burst
    df_burst = pd.DataFrame().assign(burst=data["burst"])

    #Suppresion données vides
    df_burst = df_burst.dropna()

    #Suppresion données sans caractères
    df_burst = df_burst[df_burst['burst'].str.strip().astype(bool)]

    #Création du modèle
    documents = [TaggedDocument(words=doc.split(),tags=[i]) for i,doc in enumerate(df_burst['burst'])]
    d2v_model = Doc2Vec(min_count=1)
    d2v_model.build_vocab(documents)

    vecteurs = np.vstack((d2v_model.dv[0],d2v_model.dv[1]))
    i=2
    while i<len(d2v_model.dv):
        vecteurs = np.vstack((vecteurs,d2v_model.dv[i]))
        i+=1

    
    df_vecteurs = pd.DataFrame(vecteurs, columns = ["vecteur" + str(i) for i in range(100)])

    df_kmeans = data.dropna(subset = ['burst'])
    df_kmeans = df_kmeans[df_kmeans['burst'].str.strip().astype(bool)]

    df_kmeans['duree_pause'] = df_kmeans['duree_pause'].fillna(0)

    i=0
    while i < 100:
        df_kmeans["vecteur"+str(i)]= vecteurs[:,i]
        i+=1

    df_kmeans = df_kmeans._get_numeric_data()

    df_kmeans = df_kmeans.drop(['session','redacteur','debut_burst','longueur_burst','startPos','endPos','docLength'], axis=1)

    df_kmeans = df_kmeans[df_kmeans['duree_pause'] >= 2.0]

    distortions = []
    K = range(1,10)
    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit_predict(df_kmeans)
        distortions.append(kmeanModel.inertia_)


    km = KMeans(n_clusters=5)
    df_kmeans["cluster"]=km.fit_predict(df_kmeans)
    df_kmeans[df_kmeans.cluster==0].shape

    df_cluster = data.dropna(subset = ['burst'])
    df_cluster = df_cluster[df_cluster['burst'].str.strip().astype(bool)]
    df_cluster['duree_pause'] = df_cluster['duree_pause'].fillna(0)
    df_cluster = df_cluster[df_cluster['duree_pause'] >= 2.0]

    df_cluster["cluster"]=df_kmeans["cluster"]

    df_cluster[df_cluster.cluster==4].shape

    df_cluster0 = df_cluster[df_cluster.cluster==0]
    df_cluster1 = df_cluster[df_cluster.cluster==1]
    df_cluster2 = df_cluster[df_cluster.cluster==2]
    df_cluster3 = df_cluster[df_cluster.cluster==3]
    df_cluster4 = df_cluster[df_cluster.cluster==4]
# Create a list of dictionaries for each cluster with the specified format
    clusters = []
    for i in range(5):
        df_cluster_i = df_cluster[df_cluster.cluster==i]
        repeated = []
        for j, b in enumerate(df_cluster_i["burst"]):
            cluster_dict = {}
            if b in repeated:
                k = df_cluster_i[df_cluster_i["burst"] == b].index[repeated.count(b)]
            else: 
                k = df_cluster_i[df_cluster_i["burst"] == b].index[0]
            cluster_dict["burstID"] = k
            cluster_dict["clusterID"] = i
            cluster_dict["burstLength"] = float(df_cluster_i.iloc[j]["longueur_burst"])
            cluster_dict["pauseLength"] = float(df_cluster_i.iloc[j]["duree_pause"])
            cluster_dict["textContent"] = postag(df_cluster_i.iloc[j]["burst"])
            repeated.append(b)
            clusters.append(cluster_dict)
    sorted_clusters = sorted(clusters, key=lambda k: k['burstID'])

    for i in range(len(sorted_clusters)):
        sorted_clusters[i]['burstID'] = i+1
    
    return sorted_clusters


def postag(text):
    tex = nlp(text)
    l = []
    for token in tex:
        new_string = token.text.replace("'", "")
        l.append([new_string, token.pos_])
    return l