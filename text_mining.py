from unidecode import unidecode
import re 
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from collections import defaultdict
with open("datasets/article.txt", "r", encoding="utf-8") as file:
    raw_text = file.read().lower()
    
STOP_WORDS = set(
    """
a à â abord afin ah ai aie ainsi ait allaient allons
alors anterieur anterieure anterieures antérieur antérieure antérieures
apres après as assez attendu au
aupres auquel aura auraient aurait auront
aussi autre autrement autres autrui aux auxquelles auxquels avaient
avais avait avant avec avoir avons ayant

bas basee bat

c' c’ ça car ce ceci cela celle celle-ci celle-la celle-là celles celles-ci celles-la celles-là
celui celui-ci celui-la celui-là cent cependant certain certaine certaines certains certes ces
cet cette ceux ceux-ci ceux-là chacun chacune chaque chez ci cinq cinquantaine cinquante
cinquantième cinquième combien comme comment compris concernant

d' d’ da dans de debout dedans dehors deja dejà delà depuis derriere
derrière des desormais desquelles desquels dessous dessus deux deuxième
deuxièmement devant devers devra different differente differentes differents différent
différente différentes différents dire directe directement dit dite dits divers
diverse diverses dix dix-huit dix-neuf dix-sept dixième doit doivent donc dont
douze douzième du duquel durant dès déja déjà désormais

effet egalement eh elle elle-meme elle-même elles elles-memes elles-mêmes en encore
enfin entre envers environ es ès est et etaient étaient etais étais etait était
etant étant etc etre être eu eux eux-mêmes exactement excepté également

fais faisaient faisant fait facon façon feront font

gens

ha hem hep hi ho hormis hors hou houp hue hui huit huitième
hé i il ils importe

j' j’ je jusqu jusque juste

l' l’ la laisser laquelle le lequel les lesquelles lesquels leur leurs longtemps
lors lorsque lui lui-meme lui-même là lès

m' m’ ma maint maintenant mais malgre malgré me meme memes merci mes mien
mienne miennes miens mille moi moi-meme moi-même moindres moins
mon même mêmes

n' n’ na ne neanmoins neuvième ni nombreuses nombreux nos notamment
notre nous nous-mêmes nouveau nul néanmoins nôtre nôtres

o ô on ont onze onzième or ou ouias ouste outre
ouvert ouverte ouverts où

par parce parfois parle parlent parler parmi partant
pas pendant pense permet personne peu peut peuvent peux plus
plusieurs plutot plutôt possible possibles pour pourquoi
pourrais pourrait pouvait prealable precisement
premier première premièrement
pres procedant proche près préalable précisement pu puis puisque

qu' qu’ quand quant quant-à-soi quarante quatorze quatre quatre-vingt
quatrième quatrièmement que quel quelconque quelle quelles quelqu'un quelque
quelques quels qui quiconque quinze quoi quoique

relative relativement rend rendre restant reste
restent retour revoici revoila revoilà

s' s’ sa sait sans sauf se seize selon semblable semblaient
semble semblent sent sept septième sera seraient serait seront ses seul seule
seulement seuls seules si sien sienne siennes siens sinon six sixième soi soi-meme soi-même soit
soixante son sont sous souvent specifique specifiques spécifique spécifiques stop
suffisant suffisante suffit suis suit suivant suivante
suivantes suivants suivre sur surtout

t' t’ ta tant te tel telle tellement telles tels tenant tend tenir tente
tes tien tienne tiennes tiens toi toi-meme toi-même ton touchant toujours tous
tout toute toutes treize trente tres trois troisième troisièmement très
tu té

un une unes uns

va vais vas vers via vingt voici voila voilà vont vos
votre votres vous vous-mêmes vu vé vôtre vôtres
y""".split()
) 

# NETTOYAGE
stopWords = [unidecode(sw) for sw in STOP_WORDS]
stopWords = [re.sub(r'[^a-z]+' , ' ' , word) for word in stopWords]
raw_text = re.sub(r"\bl['’]\b", " ", raw_text)
list_words = raw_text.split() 
list_word = [unidecode(word) for word in list_words]
list_word = [re.sub(r'[0-9]{4}','annee',word) for word in list_word]
list_word = [re.sub(r'[^a-z]+' , ' ' , word) for word in list_word]
#  supprimer les espaces vides dans chaque mot de la liste
list_word = [word.strip() for word in list_word if word.strip() != '']
text_cleaned = ' '.join(word for word in list_word if word not in stopWords)
text_cleaned_list = text_cleaned.split()
stemmer = SnowballStemmer('french')

text_stemmed = [" ".join([stemmer.stem(word) for word in text_cleaned.split()])]

# print(text_stemmed)


# VOCABULAIRE
vocabulaire = set(text_stemmed[0].split())

# print(text_stemmed)

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(text_stemmed)
# print(vectorizer.get_feature_names_out())
# print(X.toarray())

# BIGRAMMES

bg = list(nltk.bigrams(text_stemmed[0].split()))
# print(bg)

# TF-IDF
vectorizer_tfidf = TfidfVectorizer()
X_tfidf = vectorizer_tfidf.fit_transform(text_stemmed)
freq = defaultdict(float)
for mot in text_cleaned_list:
    freq[mot] += 1
print(freq)

from wordcloud import WordCloud
import matplotlib.pyplot as plt
wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='viridis').generate_from_frequencies(freq)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()