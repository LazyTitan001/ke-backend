import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
import logging

logger = logging.getLogger(__name__)

def train_model():
    """
    Train a new crop recommendation model
    
    Returns:
        model: Trained RandomForestClassifier model
    """
    logger.info("Training new model...")
    
    # Load the dataset
    df = pd.read_csv('Crop_recommendation.csv')

    # Prepare features and target
    features = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    target = df['label']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    accuracy = model.score(X_test, y_test)
    logger.info(f"Model trained with accuracy: {accuracy:.4f}")
    
    return model

def save_model(model, filepath='model.pkl'):
    """
    Save a trained model to disk
    
    Args:
        model: Trained model to save
        filepath: Path to save the model
    """
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {filepath}")

def load_model(filepath='model.pkl'):
    """
    Load a trained model from disk or train a new one if not found
    
    Args:
        filepath: Path to the model file
        
    Returns:
        model: Loaded or newly trained model
    """
    if os.path.exists(filepath):
        logger.info(f"Loading model from {filepath}")
        try:
            with open(filepath, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Training new model instead")
            model = train_model()
            save_model(model, filepath)
            return model
    else:
        logger.info(f"Model file {filepath} not found")
        model = train_model()
        save_model(model, filepath)
        return model
