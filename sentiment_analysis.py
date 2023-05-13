from transformers import pipeline

def init():
    # Initialize your sentiment analysis model here
    global sentiment_model
    sentiment_model = pipeline('sentiment-analysis')

def analyze(user_input):
    # Implement your sentiment analysis function here
    result = sentiment_model(user_input)[0]
    return result['label'], result['score']
