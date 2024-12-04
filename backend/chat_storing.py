from flask_sqlalchemy import SQLAlchemy  # Ensure this is importing your Flask app correctly
from datetime import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3


app_ = Flask(__name__)
CORS(app_)

# Ensure you have an absolute path for the database file
app_.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('chat.db')}"
app_.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking (optional)

db = SQLAlchemy(app_)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(), nullable=False, unique=True)  # Ensure keywords are unique
    date_created = db.Column(db.DateTime, default=datetime.now)
    messages = db.relationship('Message', backref='chat', lazy=True, primaryjoin="Chat.keyword == Message.keyword")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable = False)
    keyword = db.Column(db.String(), db.ForeignKey('chat.keyword'), nullable=False)  # Link via keyword
    user_id = db.Column(db.Integer, default=0)  # 0 is AI
    content = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    citations = db.relationship('Citation', backref = 'message', lazy=True, primaryjoin="Message.id == Citation.messageid")
# Create the database tables

class Citation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String())
    url = db.Column(db.String(), nullable=False)
    page = db.Column(db.Integer, default = 0)
    messageid = db.Column(db.Integer, db.ForeignKey('message.id'), nullable = False)


def get_all_chat_keywords():
    """
    Retrieve a list of all keywords for all chats in the database.
    Returns:
        List of strings representing the keywords.
    """
    # Query the Chat table for all keywords
    all_chats = Chat.query.with_entities(Chat.keyword).all()
    # Extract the keywords from the result
    return [chat.keyword for chat in all_chats]

def is_keyword_existing(keyword):
    """
    Check if a given keyword exists in the database.
    
    Args:
        keyword (str): The keyword to check.
    
    Returns:
        bool: True if the keyword exists, False otherwise.
    """
    # Query the Chat table for the given keyword
    existing_chat = Chat.query.filter_by(keyword=keyword).first()
    return existing_chat is not None


def save_citations(id, citation):
    # Retrieve the chat object based on the keyword
    message = Message.query.filter_by(id=id).first()
    
    # If the chat exists, create a new message and associate it with the chat
    if message:
        citation = Citation(messageid = id, title=citation["title"], url=citation["link"], page=citation["page"])
        db.session.add(citation)
        db.session.commit()
    else:
        print("Chat with the provided keyword does not exist.")
    

def save_message(keyword, user_id, content):
    # Retrieve the chat object based on the keyword
    chat = Chat.query.filter_by(keyword=keyword).first()
    
    # If the chat exists, create a new message and associate it with the chat
    if chat:
        message = Message(keyword=keyword, user_id=user_id, content=content, date_created=datetime.now())
        db.session.add(message)
        db.session.commit()
    else:
        print("Chat with the provided keyword does not exist.")
    return message.id

def get_citations(id):
    # Retrieve messages associated with the chat identified by the keyword
    message = Message.query.filter_by(id=id).first()

    if message:
        citations = message.citations  # This will automatically use the relationship defined in the Chat model
        return [(citations.title, citations.url, citations.page, citations.id) for citation in citations]
    else:
        print("Message with provided ID does not exist.")
        return []
    
def get_messages(keyword):
    # Retrieve messages associated with the chat identified by the keyword
    chat = Chat.query.filter_by(keyword=keyword).first()

    if chat:
        messages = chat.messages  # This will automatically use the relationship defined in the Chat model
        return [(message.user_id, message.content, message.date_created, message.id, message.citations) for message in messages]
    else:
        print("Chat with the provided keyword does not exist.")
        return []

def create_chat(keyword):
    # Check if the chat already exists
    chat = Chat.query.filter_by(keyword=keyword).first()

    if chat:
        print(f"Chat with keyword '{keyword}' already exists.")
        return chat  # Optionally return the existing chat

    # If the chat doesn't exist, create a new chat
    new_chat = Chat(keyword=keyword, date_created=datetime.now())
    
    # Add the new chat to the session and commit it to the database
    db.session.add(new_chat)
    db.session.commit()

    print(f"Chat with keyword '{keyword}' has been created.")


with app_.app_context():
    print("Creating database and tables...")
    db.create_all()
    print("Database and tables created successfully!")

