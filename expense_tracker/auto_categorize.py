import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier
import joblib
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import string
import re


class TextPreprocessor:
    """Class for text preprocessing and feature extraction."""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def get_wordnet_pos(self, word):
        """Map POS tag to first character lemmatize() accepts"""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)
    
    def preprocess_text(self, text):
        """Preprocess text with advanced NLP techniques."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Tokenization
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token, self.get_wordnet_pos(token))
                 for token in tokens
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)

class ExpenseCategorizer:
    """
    A class to automatically categorize expenses based on their descriptions
    using a combination of Naive Bayes and SVM algorithms with advanced NLP.
    """
    
    def __init__(self, model_path='expense_model.pkl'):
        self.model_path = model_path
        self.categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health', 'Other']
        self.model = None
        self.preprocessor = TextPreprocessor()
        
        # Try to load an existing model
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"Model loaded from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
    
    def create_advanced_features(self, text_series):
        """Create advanced features from text descriptions."""
        # Basic preprocessing
        processed_texts = text_series.apply(self.preprocessor.preprocess_text)
        
        # Create TF-IDF features with n-grams and custom parameters
        tfidf = TfidfTransformer(
            smooth_idf=True,
            use_idf=True
        )
        
        # Create count vectors with advanced parameters
        count_vec = CountVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 3),
            strip_accents='unicode'
        )
        
        return processed_texts
    
    def train(self, csv_file):
        """Train the model using expense data from a CSV file."""
        try:
            # Load data
            df = pd.read_csv(csv_file)
            
            # Check if we have enough data
            if len(df) < 10:
                print("Not enough data to train the model. Need at least 10 entries.")
                return False
            
            # Ensure required columns exist
            if 'description' not in df.columns or 'category' not in df.columns:
                print("CSV must contain 'description' and 'category' columns.")
                return False
            
            # Prepare data with advanced features
            X = self.create_advanced_features(df['description'])
            y = df['category'].values  # Set y parameter with respect to x
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Create enhanced pipelines for each classifier
            nb_pipeline = Pipeline([
                ('vect', CountVectorizer(
                    max_features=5000,
                    min_df=2,
                    max_df=0.95,
                    ngram_range=(1, 3),
                    strip_accents='unicode'
                )),
                ('tfidf', TfidfTransformer(
                    smooth_idf=True,
                    use_idf=True
                )),
                ('clf', MultinomialNB(alpha=0.1))
            ])
            
            svm_pipeline = Pipeline([
                ('vect', CountVectorizer(
                    max_features=500,
                    min_df=2,
                    max_df=0.95,
                    ngram_range=(1, 3),
                    strip_accents='unicode'
                )),
                ('tfidf', TfidfTransformer(
                    smooth_idf=True,
                    use_idf=True
                )),
                ('clf', SVC(
                    probability=True,
                    kernel='rbf',
                    C=1
                )),
                
            ])
            
            # Create ensemble model with weights
            self.model = VotingClassifier(
                estimators=[
                    ('nb', nb_pipeline),
                    ('svm', svm_pipeline)
                ],
                voting='soft',
                weights=[1, 2]  # Give more weight to SVM
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            accuracy = self.model.score(X_test, y_test)
            print(f"Model trained with accuracy: {accuracy:.2f}")
            
            # Save the model
            joblib.dump(self.model, self.model_path)
            print(f"Model saved to {self.model_path}")
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict_category(self, description):
        """Predict the category for a given expense description."""
        if self.model is None:
            return 'Other'
        
        try:
            # Preprocess the description
            processed_desc = self.preprocessor.preprocess_text(description)
            
            # Make prediction
            prediction = self.model.predict([processed_desc])[0]
            probabilities = self.model.predict_proba([processed_desc])[0]
            max_prob = max(probabilities)
            
            # If confidence is too low, return 'Other'
            if max_prob < 0.4:
                return 'Other'
                
            return prediction
        except Exception as e:
            print(f"Error predicting category: {e}")
            return 'Other'
    
    def get_confidence(self, description):
        """Get the confidence score for the prediction."""
        if self.model is None:
            return 0.0
        
        try:
            # Preprocess the description
            processed_desc = self.preprocessor.preprocess_text(description)
            
            probabilities = self.model.predict_proba([processed_desc])[0]
            return max(probabilities)
        except Exception as e:
            print(f"Error getting confidence: {e}")
            return 0.0

# Example usage
if __name__ == "__main__":
    categorizer = ExpenseCategorizer()
    
    # Train if we have data
    if os.path.exists('expenses.csv'):
        categorizer.train('expenses.csv')
    
    # Test predictions
    test_descriptions = [
        "Starbucks coffee and breakfast sandwich",
        "Monthly unlimited metro pass",
        "Electric and water utility payment",
        "Movie tickets at AMC theater",
        "New winter jacket from Nike store"
    ]
    
    for desc in test_descriptions:
        category = categorizer.predict_category(desc)
        confidence = categorizer.get_confidence(desc)
        print(f"Description: '{desc}' → Category: '{category}' (Confidence: {confidence:.2f})")