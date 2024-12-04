from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
import asyncio
import threading
from un_scrape import c_call, c_create, c_del, c_reset, scraper  # Import scraped links
from un_main import main as chatbot_main, ota_speech_chat_completion, ask_q # Import chatbot functions
from chat_storing import app_, get_messages, save_message, create_chat, is_keyword_existing, get_all_chat_keywords, save_citations, get_citations, delete_chat
  # Enable Cross-Origin Resource Sharing (CORS)


# Endpoint to fetch document links
@app_.route('/scrape', methods=['POST'])
def scrape():    
    data = request.get_json()
    name = data.get('keyword', '')
    subject = data.get('subject', '')
    if not subject:
        return jsonify({'error': 'No database provided'}), 404
    if is_keyword_existing(name):
        return jsonify({
            'keyword': name
        })
    create_chat(str(name))
    name, error = asyncio.run(scraper(subject, name))
    if error == 1:
        delete_chat(name)
        return jsonify({'error': 'Provided databse does not exist'})
    print("hi")
    print("bye")
    return jsonify({'keyword': name})


@app_.route('/list-collections', methods=['GET'])
def collection_list(): 
    lst = get_all_chat_keywords()
    return jsonify({'collectionList': lst,
                            })


'''
@app_.route('/get-collection', methods=['POST'])
def get_collection():
    data = request.get_json()
    col = data.get('keyword', '')
    if not col:
        return jsonify({'error': 'No collection provided'}), 400
    collection = asyncio.run(c_call(col))
    messages = chat_history()
    return jsonify({'messages': messages},
                   {'collection': collection})
'''

@app_.route('/del-collection', methods=['POST'])
def del_collection():
    data = request.get_json()
    keyword = data.get('keyword', '')
    if not keyword:
        return jsonify({'error': 'No collection provided'}), 400
    delete_chat(keyword)
    c_del(keyword)
    return jsonify({'keyword': keyword})


# Endpoint to ask a question
@app_.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    user_question = data.get('question', '')
    keyword = data.get('keyword', '')
    history = data.get('history', [])
    messages = data.get('test', [])
    print(f'user question: {user_question}')
    print(messages)
    print("NICE PEOPLE")
    print(history)
    if not user_question:
        return jsonify({'error': 'No question provided'}), 400
    if not keyword:
        return jsonify({'error': 'No database provided'}), 404
    # Run the chatbot logic in an asynchronous thread
    response = asyncio.run(ask_q(user_question, keyword, history))
    # print(response)
    return jsonify({'answer': response[0],
                    'citation' : response[1]
                    })

# Async function to process the question

@app_.route('/chat-history', methods=['POST'])
def chat_history():
    data = request.get_json()
    keyword = data.get('keyword', '')
    print(keyword)
    if not keyword:
        return jsonify({'error': 'No chat provided'}), 400
    # Fetch messages
    messages = get_messages(keyword)
    # Format into JSON
    formatted_messages = [
        {'role': role, 'content': content, 'timestamp': timestamp, 'id' : id, 
         'citations' : [{'title': citation.title, 'url': citation.url, 'page': citation.page, 'id': citation.id} for citation in citations]}
        for role, content, timestamp, id, citations in messages
    ]
    print(type(formatted_messages))
    return jsonify({'messages': formatted_messages})

@app_.route('/chat-save', methods=['POST'])
def save_to_chat():
    data = request.get_json()
    keyword = data.get('keyword', '')
    content = data.get('content', [])
    citations = data.get('citations', [])
    print(keyword)
    if not keyword:
        return jsonify({'error': 'No chat provided'}), 400
    if not content:
        return jsonify({'error': 'No content provided'}), 401
    save_message(keyword, 1, content[0])
    id = save_message(keyword, 0, content[1])
    if citations:
        for citation in citations:
            save_citations(id, citation)
    return ({'keyword': keyword})

# Run the chatbot scraping process in a background thread
def start_chatbot():
    asyncio.run(chatbot_main())

if __name__ == '__main__':
    threading.Thread(target=start_chatbot).start()  # Start chatbot in background
    app_.run(debug=True)
