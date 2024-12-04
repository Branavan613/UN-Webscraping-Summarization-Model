import asyncio
import os
from groq import AsyncGroq
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import ollama
import chromadb
from dotenv import load_dotenv
from chromadb.config import Settings
from un_scrape import c_call

# Calls the PersistentClient Vector Store


async def multiquery(client, model, user_question):
    """
    This function takes the initial user question and reinterprets it into 3 more specific questions. In the case that a user's question is too 
    broad or bland, these new question will create a more accurate search radius and will pull more relevant chunks of data
    client (Groq): The Groq client used to interact with the untrained model.
    model (str): The name of the untrained model.
    user_question (str): The question asked by the user.
    Returns:
    list: A list of 3 relevant questions.
    """
    query_prompt = f'''
    Your task is to generate 3 different search queries that aim to answer the user question from multiple perspectives. Each query MUST tackle the question from a different viewpoint, yet be unbiased. We want to get a variety of RELEVANT search results. Provide these alternative questions seperated by newlines.
    Your answer should be depicted in the format shown only between the angled brackets:
    <
    query 1
    query 2
    query 3
    >
    Original question: {user_question}
    '''
    chat_completion = await client.chat.completions.create(
        messages= [
            {"role": "system", "content" : query_prompt}
        ],
        model=model,
        temperature = 0,
        stream = False
    )
    response = chat_completion.choices[0].message.content
    # print(response)
    response = response.split("\n")
    return response[1:4]


async def ota_speech_chat_completion(client, model, conversation_history, relevant_excerpts):
    """
    This function generates a response to the user's question using a pre-trained model.
    Parameters:
    client (Groq): The Groq client used to interact with the pre-trained model.
    model (str): The name of the pre-trained model.
    conversation_history (dict): A dictionary that holds all the previous questions from the user and the previous responses from the model
    Returns:
    dict: A dictionary containing the response to the user's question in .choices[0].delta.content.
    """
    """
    conference docs:
    You are teaching Sri Lankan history. Given the user's question and relevant excerpts from
    articles regarding Tamil and Sri Lankan history, provide concise answers in a way understandable
    to someone with no prior knowledge on the subject. When applicable, make use of numeric statistics
    present in the excerpt and provide precise answers. However, do not explicitly mention the excerpt.
    Make sure your tone is serious and informational: no exclamation marks.
    """
    system_prompt = '''
    You are an AI assistant analyzing United Nations Documents. Given the user's question and relevant excerpts from
    articles, provide concise answers based solely on the context provided in a human tone. When applicable, make use of specific numeric statistics
    present in the excerpt and provide precise answers. Include direct quotations from the text.
    Make sure your tone is serious and informational: no exclamation marks.
    Most importantly, DO NOT EXTRAPOLATE FROM THE DATA. make all answers 500 words max.
    AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
    If the context does not provide the answer to the question, the NDIS assistant will say, "I'm sorry, but I don't know the answer to that question".
    AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
    AI assistant will not invent anything that is not drawn directly from the context.
    AI assistant will be as specific as possible in its answers.
    '''
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": relevant_excerpts}
        ]
    
    for role, content in conversation_history:
        messages.append({"role": role, "content": content})
    chat_completion = await client.chat.completions.create(
        messages= messages,
        model=model,
        temperature = 0, #randomness of model's answers set to 0
        stream = True 

    )
    return chat_completion

async def main():
    load_dotenv()
    """
    This is the main function that runs the application. It initializes the Groq client, 
    retrieves relevant excerpts from articles based on the user's question,
    generates a response to the user's question using a pre-trained model, and displays the response.
    """
    model = 'llama3-8b-8192'

    groq_api_key = os.getenv('GROQ_API_KEY')
    groq_client = AsyncGroq(api_key=groq_api_key)
    
    multiline_text = """
    Welcome! Ask me any question about Sri Lankan history and using information from hundreds of news reports, articles, and papers, will answer whatever question you have. I was built to provide specific information from a unbias point of view on historical events.
    """
    print(multiline_text)
    

async def ask_q(question, keyword, conversation_history):
    model = 'llama3-8b-8192'
    collection = await c_call(keyword)

    groq_api_key = os.getenv('GROQ_API_KEY')
    groq_client = AsyncGroq(api_key=groq_api_key)

    # Get the user's question
    citation = []
    user_question = question

    if user_question:
        conversation_history.append(("user", user_question))
        # Generate multiquery for user question
        multiqueries =  await multiquery(groq_client, model, user_question)
        # print(multiqueries)
        
        data = []
        #there are instances where the untrained model will not deal with sensitive topics. In that case, just pass the original question into the trained RAG model
        if multiqueries:
            for query in multiqueries:
                #create embedding for each prompt
                q = ollama.embeddings(
                    prompt=query,
                    model="nomic-embed-text"
                )
                query_embedding = q["embedding"]

                # Query the collection for the 2 most relevant documents
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=2
                )
                # print("\n\n".join(results['documents'][0]))
                
                citation.append(results["metadatas"][0][0])
                data.append("\n\n".join(results['documents'][0]))
            # Extract the relevant excerpts from the results    
            data = "\n\n".join(data)
        else:
            response = ollama.embeddings(
            prompt=user_question,
            model="nomic-embed-text"
            )
            query_embedding = response["embedding"]

            # Query the collection for the most relevant documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=4
            )
            # Extract the relevant excerpts from the results
            data = "\n\n".join(results['documents'][0])
        # Generate a response using the pre-trained model
        response = await ota_speech_chat_completion(groq_client, model, conversation_history, data)
        stream = []
        async for chunk in response:
            block = str(chunk.choices[0].delta.content)
            if "None" in block:
                break
            else:
                print(block, end="")
                stream.append(block)
                stream_str = "".join(stream)
        # add chatbot answer to context
        return [stream_str, citation]

if __name__ == "__main__":
    asyncio.run(main())
