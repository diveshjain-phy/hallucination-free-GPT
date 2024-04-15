from googlesearch import search
import requests
import io
import os
import PyPDF2
from openai import OpenAI
client = OpenAI(api_key='{CLIENT ID}')

def small_answer_this(query, c1,temp=0.3,topp=0.3):
    response = client.chat.completions.create(
  model="gpt-3.5-turbo-16k-0613",
  messages=[
    {
      "role": "system",
      "content": "based on the query and given context, in 3 points present key features of the context relevant to the query"
    },
    {
      "role": "user",
      "content": "in 3 points present key features of the context relevant to the query. My query is: "+str(query)+", refer to the following context while answering question"+str(c1)
    }
  ],
  temperature=int(temp),
  max_tokens=256,
  top_p=int(topp),
presence_penalty = 0.2,
    frequency_penalty = 0.2,
)
    reply_content = response.choices[0].message.content
    return reply_content

def download_pdf_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        return None

def extract_paragraphs_from_pdf(quest,pdf_file, tag_words):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    paragraphsx = []
    
    for page in pdf_reader.pages:
        text = page.extract_text()
        page_paragraphs = text.split("\n\n")
        
        for paragraph in page_paragraphs:
            if all(tag_word.lower() in paragraph.lower() for tag_word in tag_words):
                paragraphsx.append({small_answer_this(quest,paragraph)})
    
    return paragraphsx
def arxiv_search(quest,query,tag_words):
    paragraphs = []
    for url in search(query, tld="co.in", num=10, stop=10, pause=2):
        if "arxiv.org" in url:
            print("arXiv URL:", url)
            
            # Download the PDF file
            pdf_url = url.replace("/abs/", "/pdf/") + ".pdf"
            pdf_file = download_pdf_file(pdf_url)
            
            if pdf_file:
                # Extract paragraphs containing all the tag words
                paragraphsxx = extract_paragraphs_from_pdf(quest,pdf_file, tag_words)
                
                if paragraphsxx:
                    print(f" yes there are Paragraphs containing all the tag words: {', '.join(tag_words)}")
                    paragraphs.append(paragraphsxx)
                    #print(paragraphsxx)
                else:
                    print(f"No paragraphs found containing all the tag words: {', '.join(tag_words)}")
                
                # Close the temporary PDF file
                pdf_file.close()
            else:
                print("Failed to download the PDF file.")
            
    return paragraphs

def axanswer_this(query,mod, tl, gsearch, tags, temp=0.3, topp=0.5):
    context = arxiv_search(query,gsearch,tags)
    print("----------------------------")
    if mod==3:
        modelx = 'gpt-3.5-turbo-16k-0613'
    else:
        modelx = "gpt-4-turbo-2024-04-09"
    print(f"GPT {modelx} response")
    
    response = client.chat.completions.create(
        model= modelx,
        messages=[
            {
                "role": "system",
                "content": "The context of response is presented in the prompt.  You are crisp, mathematically driven, and extremely insightful. You are answering questions to a junior professor so your answers should be accordingly technical. Write down your thoughts while writing the answers."
            },
            {
                "role": "user",
                "content": f"{query}\n To set the context of the query, I am providing the relevant text here here: {context}"
            }
        ],
        temperature=float(temp),
        max_tokens=int(tl),
        top_p=float(topp),
        presence_penalty=0.2,
        frequency_penalty=0.2,
    )
    reply_content = response.choices[0].message.content
    return reply_content,context

ans, context = axanswer_this("{query}",3,512, "{relevant google search query}",[{expected keywords contained in the answer}])
print(f"{ans}")
