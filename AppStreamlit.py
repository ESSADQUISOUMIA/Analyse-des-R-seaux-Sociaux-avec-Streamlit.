import streamlit as st
import tweepy
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

# Configuration
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHwIxwEAAAAAWDFNr1kAimoo912CCwASC%2Fh6CII%3Djf5Up2c3BTod8j7n9hTfRBltPVji0WterZN8f0KsM1deUY9cvs" #L'API impose une limite de 100 tweets par requête.

# Authentification Twitter
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def get_tweets(query, max_results=100):
    tweets = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=['created_at', 'lang'])
    return tweets.data if tweets.data else []

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'positif'
    elif analysis.sentiment.polarity < 0:
        return 'négatif'
    else:
        return 'neutre'

def detect_trends(tweets):
    words = [word for tweet in tweets for word in tweet.text.lower().split() if len(word) > 3]
    return Counter(words).most_common(10)

def main():
    st.set_page_config(page_title="Analyse des Réseaux Sociaux", page_icon="📊", layout="wide")
    st.title("Plateforme de Surveillance et d'Analyse des Réseaux Sociaux")

    query = st.text_input("Entrez un terme de recherche:", "python")
    max_results = st.slider("Nombre de tweets à analyser:", min_value=10, max_value=100, value=30, step=10)

    if st.button("Analyser"):
        with st.spinner('Récupération et analyse des tweets...'):
            tweets = get_tweets(query, max_results)

            if not tweets:
                st.error("Aucun tweet trouvé. Vérifiez votre requête et vos autorisations API.")
                return

            sentiments = Counter(analyze_sentiment(tweet.text) for tweet in tweets)
            trends = detect_trends(tweets)

            # Affichage des résultats
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Analyse des Sentiments")
                fig, ax = plt.subplots()
                ax.bar(sentiments.keys(), sentiments.values(), color=['green', 'red', 'gray'])
                ax.set_ylabel("Nombre de tweets")
                ax.set_title("Répartition des sentiments")
                st.pyplot(fig)

            with col2:
                st.subheader("Tendances Détectées")
                trend_df = pd.DataFrame(trends, columns=['Mot', 'Fréquence'])
                st.bar_chart(trend_df.set_index('Mot'))

            st.subheader("Tweets Récents")
            for tweet in tweets[:10]:
                st.text_area(f"Tweet du {tweet.created_at}", tweet.text, height=100)

            # Téléchargement des données
            csv = pd.DataFrame([(tweet.text, analyze_sentiment(tweet.text), tweet.created_at) for tweet in tweets],
                               columns=['Tweet', 'Sentiment', 'Date'])
            st.download_button(
                label="Télécharger les données en CSV",
                data=csv.to_csv(index=False).encode('utf-8'),
                file_name='tweets_analysis.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()