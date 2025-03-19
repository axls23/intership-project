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
from sklearn.model_selection import GridSearchCV
import logging
from datetime import datetime
import json

# Configure logging
def setup_logger():
    """Setup logger with custom format and handlers"""
    logger = logging.getLogger('ExpenseCategorizerLogger')
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler for detailed logging
    file_handler = logging.FileHandler(
        f'logs/expense_categorizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for basic info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters and add them to handlers
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class TextPreprocessor:
    """Class for text preprocessing and feature extraction."""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.logger = logging.getLogger('ExpenseCategorizerLogger')
        
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
        """Preprocess text with advanced NLP techniques and logging."""
        self.logger.debug(f"Starting preprocessing for text: {text}")
        
        # Convert to lowercase
        text = text.lower()
        self.logger.debug(f"After lowercase: {text}")
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        self.logger.debug(f"After special char removal: {text}")
        
        # Tokenization
        tokens = word_tokenize(text)
        self.logger.debug(f"After tokenization: {tokens}")
        
        # Remove stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                lemmatized = self.lemmatizer.lemmatize(token, self.get_wordnet_pos(token))
                processed_tokens.append(lemmatized)
                
        self.logger.debug(f"After stopword removal and lemmatization: {processed_tokens}")
        return ' '.join(processed_tokens)

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
        self.logger = logging.getLogger('ExpenseCategorizerLogger')
        
        # Performance metrics dictionary
        self.metrics = {
            'predictions': [],
            'confidences': [],
            'categories': {},
            'errors': [],
            'training_history': []
        }
        
        # Initialize category metrics
        for category in self.categories:
            self.metrics['categories'][category] = {
                'total': 0,
                'correct': 0,
                'incorrect': 0,
                'avg_confidence': 0.0
            }
        
        # Try to load an existing model
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.logger.info(f"Model loaded from {model_path}")
            except Exception as e:
                self.logger.error(f"Error loading model: {e}")
    
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
                X, y, test_size=0.2, random_state=50
            )
            
            # Enhanced parameter grids for better tuning
            nb_param_grid = {
                'vect__max_features': [3000, 5000, 8000],
                'vect__min_df': [1, 2, 3],
                'vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
                'tfidf__use_idf': [True, False],
                'clf__alpha': [0.001, 0.01, 0.1, 0.5]
            }

            svm_param_grid = {
                'vect__max_features': [3000, 5000, 8000],
                'vect__min_df': [1, 2, 3],
                'vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
                'tfidf__use_idf': [True, False],
                'clf__C': [0.1, 1.0, 10.0],
                'clf__kernel': ['linear', 'rbf'],
                'clf__gamma': ['scale', 'auto', 0.1, 1.0]
            }

            # Create base pipelines
            nb_pipeline = Pipeline([
                ('vect', CountVectorizer()),
                ('tfidf', TfidfTransformer()),
                ('clf', MultinomialNB())
            ])
            
            svm_pipeline = Pipeline([
                ('vect', CountVectorizer()),
                ('tfidf', TfidfTransformer()),
                ('clf', SVC(probability=True))
            ])

            # Perform GridSearchCV with cross-validation
            print("Tuning Naive Bayes model...")
            nb_grid = GridSearchCV(
                nb_pipeline, 
                nb_param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            nb_grid.fit(X_train, y_train)
            print(f"Best NB parameters: {nb_grid.best_params_}")
            print(f"Best NB CV accuracy: {nb_grid.best_score_:.3f}")

            print("\nTuning SVM model...")
            svm_grid = GridSearchCV(
                svm_pipeline,
                svm_param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            svm_grid.fit(X_train, y_train)
            print(f"Best SVM parameters: {svm_grid.best_params_}")
            print(f"Best SVM CV accuracy: {svm_grid.best_score_:.3f}")

            # Create ensemble with best models
            self.model = VotingClassifier(
                estimators=[
                    ('nb', nb_grid.best_estimator_),
                    ('svm', svm_grid.best_estimator_)
                ],
                voting='soft',
                weights=[1, 2]  
            )

            # Final training
            self.model.fit(X_train, y_train)
            
            # Evaluate
            accuracy = self.model.score(X_test, y_test)
            print(f"\nFinal model accuracy: {accuracy:.3f}")
            
            # Save the model
            joblib.dump(self.model, self.model_path)
            print(f"Model saved to {self.model_path}")
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
        
    def log_prediction(self, description, predicted_category, confidence, actual_category=None):
        """Log prediction details and update metrics"""
        prediction_info = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'predicted_category': predicted_category,
            'confidence': confidence,
            'actual_category': actual_category
        }
        
        self.metrics['predictions'].append(prediction_info)
        self.metrics['confidences'].append(confidence)
        
        if actual_category:
            cat_metrics = self.metrics['categories'][predicted_category]
            cat_metrics['total'] += 1
            if predicted_category == actual_category:
                cat_metrics['correct'] += 1
            else:
                cat_metrics['incorrect'] += 1
            cat_metrics['avg_confidence'] = (cat_metrics['avg_confidence'] * (cat_metrics['total'] - 1) + confidence) / cat_metrics['total']
        
        self.logger.debug(json.dumps(prediction_info))
    
    def predict_category(self, description):
        """Predict category with logging"""
        if self.model is None:
            self.logger.warning("No model loaded, returning 'Other'")
            return 'Other'
        
        try:
            self.logger.debug(f"Processing description: {description}")
            processed_desc = self.preprocessor.preprocess_text(description)
            
            if not processed_desc:
                self.logger.warning("Empty processed description")
                return 'Other'
            
            self.logger.debug(f"Processed description: {processed_desc}")
            
            prediction = self.model.predict([processed_desc])[0]
            probabilities = self.model.predict_proba([processed_desc])[0]
            max_prob = max(probabilities)
            
            self.logger.debug(f"Raw prediction: {prediction}, Confidence: {max_prob}")
            
            # Log prediction details
            self.log_prediction(description, prediction, max_prob)
            
            if max_prob < 0.45:
                self.logger.info(f"Low confidence ({max_prob:.2f}) - defaulting to 'Other'")
                return 'Other'
            
            self.logger.info(f"Predicted category: {prediction} with confidence: {max_prob:.2f}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting category: {e}", exc_info=True)
            self.metrics['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'description': description
            })
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
    
    def save_metrics(self, filepath='logs/metrics.json'):
        """Save current metrics to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            self.logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def get_performance_report(self):
        """Generate performance report"""
        report = {
            'total_predictions': len(self.metrics['predictions']),
            'average_confidence': np.mean(self.metrics['confidences']) if self.metrics['confidences'] else 0,
            'category_performance': self.metrics['categories'],
            'error_rate': len(self.metrics['errors']) / len(self.metrics['predictions']) if self.metrics['predictions'] else 0
        }
        return report

# Example usage
if __name__ == "__main__":
    # Setup logging
    logger = setup_logger()
    logger.info("Starting expense categorizer")
    
    categorizer = ExpenseCategorizer()
    
    # Train if we have data
    if os.path.exists('expenses.csv'):
        categorizer.train('expenses.csv')
    
    # Test predictions with logging
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
        logger.info(f"Description: '{desc}' → Category: '{category}' (Confidence: {confidence:.2f})")
    
    # Save metrics and generate report
    categorizer.save_metrics()
    performance_report = categorizer.get_performance_report()
    logger.info(f"Performance Report: {json.dumps(performance_report, indent=2)}")