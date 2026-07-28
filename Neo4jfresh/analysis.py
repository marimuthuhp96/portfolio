#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
print(pd.__version__)


# In[3]:


import pandas as pd




# In[4]:


df = pd.read_csv("Restaurant_Reviews.csv")
df.head()


# In[5]:


df.columns


# In[6]:


df.shape


# In[7]:


df.isnull().sum()


# In[8]:


df = df.drop(columns=["7514"])


# In[9]:


df.columns


# In[10]:


df = df.dropna(subset=["Review"])


# In[11]:


df["Reviewer"] = df["Reviewer"].fillna("Anonymous")


# In[12]:


df = df.dropna(subset=["Rating"])


# In[13]:


df["Metadata"] = df["Metadata"].fillna("Unknown")
df["Time"] = df["Time"].fillna("Unknown")


# In[14]:


df.isnull().sum()


# In[15]:


df["Review"].head(3)


# In[16]:


import pandas as pd
import re
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.util import ngrams

nltk.download("wordnet")
nltk.download("punkt")


# In[17]:


class ReviewNLPProcessor:

    def __init__(self, df):
        """
        Initialize with dataset
        """
        self.df = df
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

    def preprocess_text(self, text):
        if not isinstance(text, str):
              return ""
        text = text.lower()
        text = re.sub(r"[^a-z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    def apply_preprocessing(self):
        """
        Apply preprocessing to Review column
        """
        self.df["clean_review"] = self.df["Review"].apply(self.preprocess_text)
        return self.df

    def lemmatize_text(self, text):
        """
        Convert words to base form
        """
        return " ".join([self.lemmatizer.lemmatize(word) for word in text.split()])
    def apply_lemmatization(self):
        """
        Apply lemmatization to clean_review
        """
        self.df["lemmatized_review"] = self.df["clean_review"].apply(self.lemmatize_text)
        return self.df
    def stem_text(self, text):
        """
        Apply stemming (mainly for opinion words)
        """
        return " ".join([self.stemmer.stem(word) for word in text.split()])
    def apply_stemming(self):
        """
        Apply stemming to lemmatized_review
        """
        self.df["stemmed_review"] = self.df["lemmatized_review"].apply(self.stem_text)
        return self.df
    def generate_ngrams(self, text, n):
        words = text.split()
        return [" ".join(g) for g in ngrams(words, n)]
    def apply_ngrams(self):
        self.df["bigrams"] = self.df["lemmatized_review"].apply(lambda x: self.generate_ngrams(x, 2))
        self.df["trigrams"] = self.df["lemmatized_review"].apply(lambda x: self.generate_ngrams(x, 3))
        return self.df
    def run_full_pipeline(self):
        self.apply_preprocessing()
        self.apply_lemmatization()
        self.apply_stemming()
        self.apply_ngrams()
        return self.df


# In[18]:


nlp_processor = ReviewNLPProcessor(df)
df_processed = nlp_processor.run_full_pipeline()
df_processed.head()


# In[19]:


df_processed.isnull().sum()


# In[20]:


import nltk
from nltk import pos_tag, word_tokenize

nltk.download("averaged_perceptron_tagger")

class FoodEntityExtractor:

    def __init__(self, dataframe):
        self.df = dataframe
        self.stop_terms = {
            "food", "service", "ambience", "staff", "place",
            "experience", "restaurant", "management"
        }

    def extract_food_candidates(self, text):
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)

        candidates = []
        current_phrase = []

        for word, tag in tagged:
            if tag.startswith("NN") or tag.startswith("JJ"):
                current_phrase.append(word)
            else:
                if len(current_phrase) > 0:
                    phrase = " ".join(current_phrase)
                    if phrase not in self.stop_terms:
                        candidates.append(phrase)
                    current_phrase = []

        if len(current_phrase) > 0:
            phrase = " ".join(current_phrase)
            if phrase not in self.stop_terms:
                candidates.append(phrase)

        return candidates

    def apply_food_extraction(self):
        self.df["food_entities"] = self.df["clean_review"].apply(
            self.extract_food_candidates
        )
        return self.df


# In[21]:


food_extractor = FoodEntityExtractor(df_processed)
df_processed = food_extractor.apply_food_extraction()

df_processed[["clean_review", "food_entities"]].head(10)


# In[22]:


class FoodEntityCleaner:

    def __init__(self, dataframe):
        self.df = dataframe

        # words that usually indicate actual dishes
        self.food_indicators = {
            "biryani", "pasta", "corn", "fish", "chicken", "mutton",
            "paneer", "fry", "masala", "soup", "starter", "drumsticks",
            "lotus", "stem", "rice", "curry", "tangdi", "tikka",
            "pulao", "kofta", "noodles", "cheese"
        }

        # words that clearly indicate NON-food concepts
        self.remove_keywords = {
            "service", "ambience", "staff", "place", "people",
            "experience", "good", "great", "nice", "excellent",
            "friend", "guy", "evening", "birthday", "team",
            "recommendation", "visit", "waiter", "caption",
            "lighting", "parents", "reviews", "course",
            "music", "singer", "voice", "table"
        }

        # generic food-category words (not dishes)
        self.generic_food_terms = {
            "food", "items", "options", "menu", "dishes",
            "dessert", "veg", "non", "vegetarian",
            "special", "best", "today", "time", "review",
            "meal", "lunch", "dinner", "brunch", "feast"
        }

        # verbs that indicate ordering / eating context
        self.order_verbs = {
            "ordered", "order", "try", "tried", "had",
            "served", "taste", "tasted", "having"
        }

    def is_valid_food(self, phrase, review_text):
        words = phrase.split()

        # Rule 0: must be at least 2 words
        if len(words) < 2:
            return False

        # Rule 1: reject obvious non-food terms
        for w in words:
            if w in self.remove_keywords:
                return False

        # Rule 2: reject generic food-category phrases
        for w in words:
            if w in self.generic_food_terms:
                return False

        # Rule 3: accept if known food indicator present
        for w in words:
            if w in self.food_indicators:
                return True

        # Rule 4: fallback — phrase appears in ordering context
        for verb in self.order_verbs:
            if verb in review_text:
                return True

        return False

    def clean_food_entities(self):
        cleaned_foods = []

        for idx, foods in enumerate(self.df["food_entities"]):
            review_text = self.df.iloc[idx]["clean_review"]

            valid_foods = [
                food for food in foods
                if self.is_valid_food(food, review_text)
            ]

            cleaned_foods.append(valid_foods)

        self.df["food_entities"] = cleaned_foods
        return self.df


# In[23]:


food_cleaner = FoodEntityCleaner(df_processed)
df_processed = food_cleaner.clean_food_entities()

df_processed[["clean_review", "food_entities"]].head(100)


# In[24]:


df_processed["food_entities"].explode().value_counts().head(50)


# In[25]:


class FinalFoodExtractor:

    def __init__(self, dataframe):
        self.df = dataframe

        self.food_keywords = {
            "biryani","chicken","mutton","paneer","tikka","kebab",
            "fry","fried","rice","pulao","curry","masala",
            "drumstick","drumsticks","fish","egg",
            "naan","roti","paratha","pizza","burger","pasta","noodles",
            "ice","cream","cake","dessert","sweet",
            "dal","makhani","kofta","shawarma","corn",
            "soup","starter","bbq","tandoori"
        }

        self.food_endings = {
            "biryani","fry","curry","tikka","rice",
            "masala","noodles","pasta","soup","kebab"
        }

        self.reject_words = {
            "service","ambience","place","staff","experience",
            "birthday","team","friend","visit","music",
            "price","time","table","people","waiter"
        }

    def is_food(self, phrase):
        words = phrase.split()

        # reject obvious non-food
        if any(w in self.reject_words for w in words):
            return False

        # contains food keyword
        if any(w in self.food_keywords for w in words):
            return True

        # phrase ending like "kodi fry", "mutton curry"
        if words[-1] in self.food_endings:
            return True

        return False

    def extract(self):
        final = []

        for foods in self.df["food_entities"]:
            valid = [f for f in foods if self.is_food(f)]
            final.append(list(set(valid)))

        self.df["final_foods"] = final
        return self.df


# In[26]:


fe = FinalFoodExtractor(df_processed)
df_processed = fe.extract()

df_processed[["clean_review","final_foods"]].head(1000)


# In[27]:


df_processed["Rating"] = pd.to_numeric(df_processed["Rating"], errors="coerce")


# In[28]:


def get_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating == 3:
        return "Neutral"
    else:
        return "Negative"

df_processed["sentiment"] = df_processed["Rating"].apply(get_sentiment)

df_processed[["Rating","sentiment"]].head(50)


# In[29]:


all_foods = []

for foods in df_processed["final_foods"]:
    all_foods.extend(foods)

unique_foods = sorted(set(all_foods))

for food in unique_foods:
    print(food)


# In[30]:


food_dict = {

#  Chicken items
"chicken_items":[
"chicken biryani","butter chicken","chicken curry","kadai chicken",
"chicken tikka","tandoori chicken","grilled chicken","fried chicken",
"smoky chicken","pepper chicken","chilli chicken","dragon chicken",
"chicken 65","chicken kebab","malai kebab","angara kebab","tangdi kebab",
"chicken wings","hot wings","chicken popcorn","chicken nuggets",
"chicken burger","zinger burger","double zinger burger","chicken wrap",
"chicken shawarma","chicken fried rice","chicken noodles",
"chicken rice bowl","chicken pasta","chicken lasagna","chicken pizza",
"chicken haleem","chicken dum pulao","chicken starter","chicken platter"
],

#  Mutton items
"mutton_items":[
"mutton biryani","mutton curry","mutton rogan josh","mutton masala",
"mutton keema","mutton haleem","mutton kebab","mutton galouti kebab",
"mutton mandi","mutton soup","mutton thali"
],

#  Fish & seafood
"fish_seafood":[
"fish fry","fish curry","apollo fish","fish tikka",
"grilled fish","tawa fish","fish fingers",
"prawn curry","prawns fry","butter garlic prawns",
"chilli prawns","golden fried prawns",
"seafood platter","crab curry","lobster"
],

#  Paneer items
"paneer_items":[
"paneer butter masala","paneer tikka","paneer curry",
"paneer shashlik","paneer bhurji","palak paneer",
"kadai paneer","paneer 65","paneer manchurian",
"paneer noodles","paneer fried rice","paneer roll",
"paneer sandwich", "kofta"
],

# Veg main items
"veg_items":[
"dal makhani","dal tadka","rajma","rajma chawal","chole",
"chole bhature","mix veg","dum aloo","aloo curry",
"mushroom curry","veg thali","veg combo"
],

#  Rice items
"rice_items":[
"fried rice","jeera rice","steam rice","plain rice",
"curd rice","sambar rice","bagara rice",
"veg pulao","kaju pulao","mushroom pulao",
"coconut rice","veg biryani","egg biryani",
"paneer biryani","kaju paneer biryani"
],

#  Noodles & pasta
"noodles_pasta":[
"hakka noodles","schezwan noodles","garlic noodles",
"veg noodles","chicken noodles","egg noodles",
"ramen noodles","alfredo pasta","white sauce pasta",
"red sauce pasta","penne pasta","spaghetti","lasagna"
],

#  Breads
"breads":[
"butter naan","garlic naan","tandoori roti","rumali roti",
"paratha","aloo paratha","laccha paratha","kulcha",
"pav","chapati","amritsari kulcha","lacha paratha"
],

#  Pizza & burger
"pizza_burger":[
"chicken pizza","veg pizza","margherita pizza",
"paneer pizza","pepperoni pizza","cheese pizza",
"burger","chicken burger","veg burger","zinger burger"
],

# Starters
"starters":[
"crispy corn","corn cheese balls","chilli paneer",
"spring roll","veg spring roll","chicken spring roll",
"manchurian","gobi manchurian","chicken manchurian",
"nachos","french fries","potato wedges", "kodiak fry"
],

#  Soups
"soups":[
"manchow soup","sweet corn soup","hot and sour soup",
"tomato soup","chicken soup","mutton soup",
"lemon coriander soup"
],

#  Desserts & drinks
"desserts":[
"ice cream","gulab jamun","kheer","apricot pudding",
"brownie","chocolate cake","lassi","butter milk",
"shikanji","irani chai"
]

}



# In[31]:


import re

class FinalFoodExtractor:

    def __init__(self, df, food_dict):
        self.df = df
        self.food_dict = food_dict
        self.all_foods = self.combine_foods()

    def combine_foods(self):
        all_foods = []
        for category in self.food_dict.values():
            all_foods.extend(category)

        return list(set(all_foods))

    def extract_foods_from_review(self, review):

        if not isinstance(review, str):
            return []

        review = review.lower()
        found = []

        for food in self.all_foods:
            pattern = r'\b' + re.escape(food) + r'\b'
            if re.search(pattern, review):
                found.append(food)

        return list(set(found))

    def run_extraction(self):
        self.df["final_foods"] = self.df["clean_review"].apply(self.extract_foods_from_review)
        return self.df


# In[32]:


food_model = FinalFoodExtractor(df_processed, food_dict)
df_processed = food_model.run_extraction()

df_processed[["clean_review","final_foods"]].head(1000)


# In[33]:


all_foods_extracted = []

for foods in df_processed["final_foods"]:
    all_foods_extracted.extend(foods)

unique_foods = sorted(set(all_foods_extracted))

for food in unique_foods:
    print(food)


# In[34]:


# reviews that have atleast 1 food item
reviews_with_food = df_processed[df_processed["final_foods"].apply(lambda x: len(x) > 0)]

print("Total reviews with food items:", len(reviews_with_food))


# In[35]:


import re
import spacy

class FinalFoodExtractor:

    def __init__(self, df, food_dict):
        self.df = df
        self.food_dict = food_dict
        self.all_foods = self.combine_foods()
        self.nlp = spacy.load("en_core_web_sm")   # NER model

    # combine all dictionary foods
    def combine_foods(self):
        all_foods = []
        for category in self.food_dict.values():
            all_foods.extend(category)
        return list(set(all_foods))

    # dictionary extraction
    def dict_extract(self, review):
        found = []
        for food in self.all_foods:
            pattern = r'\b' + re.escape(food) + r'\b'
            if re.search(pattern, review):
                found.append(food)
        return found

    # NER extraction
    def ner_extract(self, review):
        doc = self.nlp(review)
        ner_foods = []

        for token in doc:
            # detect possible food nouns
            if token.pos_ in ["NOUN", "PROPN"]:
                word = token.text.lower()

                # common food words filter
                if word in [
                    "biryani","burger","pizza","rice","noodles","pasta",
                    "chicken","mutton","fish","shawarma","fries","kebab",
                    "roll","thali","paneer","cake","icecream","lassi"
                ]:
                    ner_foods.append(word)

        return ner_foods

    # main extraction
    def extract_foods_from_review(self, review):

        if not isinstance(review, str):
            return []

        review = review.lower()

        dict_foods = self.dict_extract(review)
        ner_foods = self.ner_extract(review)

        final = list(set(dict_foods + ner_foods))
        return final

    def run_extraction(self):
        self.df["final_foods"] = self.df["clean_review"].apply(self.extract_foods_from_review)
        return self.df


# In[36]:


food_model = FinalFoodExtractor(df_processed, food_dict)
df_processed = food_model.run_extraction()

df_processed[["clean_review","final_foods"]].head(1000)


# In[37]:


from collections import Counter

all_foods = []
for foods in df_processed["final_foods"]:
    all_foods.extend(foods)

Counter(all_foods).most_common(20)


# In[38]:


df_exploded = df_processed.explode("final_foods")
df_exploded = df_exploded.dropna(subset=["final_foods"])

food_sentiment = df_exploded.groupby(["final_foods","sentiment"]).size().unstack(fill_value=0)
food_sentiment


# In[39]:



# In[40]:




# In[44]:




# In[ ]:




