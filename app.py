import openai
from flask import Flask, render_template, request, session
import os
import re

openai.api_key = os.environ['OPENAI_API_KEY']

app = Flask(__name__)
app.secret_key = 'secret'
def get_img(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size = '512x512',
        )
        img_url = response.data[0].url
        
    except Exception as e:
        img_url = 'https://img.freepik.com/free-vector/glitch-error-404-page-background_23-2148090004.jpg?w=1380&t=st=1681643902~exp=1681644502~hmac=06deccb0a8f3d8e848ac4f4b6d03756e7dc39b11344c9da45945193a16ecf5e8'
    return img_url

def prompt(inp,message_history, role='user'):
    message_history.append({'role':role,'content':inp})
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=message_history
    )
    reply_content = completion.choices[0].message.content
    message_history.append({'role':'assistant', 'content':reply_content})
    print(reply_content)
    return reply_content, message_history

# Define a route for the home page
@app.route('/', methods=['GET','POST'])
def index():
    # Set the title of the webpage
    title = 'Journey'
    
    # Create dictionaries to store button messages and states
    button_messages = {}
    button_states = {}
    
    # Handle GET request
    if request.method == 'GET':
        # Set the initial message history and retrieve the first response
        session['message_history'] = [{'role':'user', 'content':'You are an internactive story game bot that proposes hypothetical fantastical situations in an old arabic theme where the user needs to pick from 2-4 options that you provide. once the user picks one of those options you will then state what happens next and present new options. and this then repeats. if you understand, say, OK, and begin when I say "begin". when you preent the story and options, present just the story no further commentary, and then options like "Option 1:" "Option 2:"...etc.'},
                                      {'role':'assistant', 'content':'OK, I understand. Begin when you are ready.'}]

        # Retrieve the initial response and extract the story text and options
        message_history = session['message_history']
        reply_content, message_history = prompt('Begin', message_history)
        
        text = reply_content.split('Option 1:')[0]
        options = re.findall('Option \d:.*', reply_content)
        
        # Set up the button messages and states for each option
        for i, option in enumerate(options):
            button_messages[f'button{i+1}'] = option
            
        for button_name in button_messages:
            button_states[button_name] = False
    
            
     # Handle POST request
    message= None
    button_name = None
    if request.method == 'POST':
        # Retrieve the message history and button messages from the session
        message_history = session['message_history']
        button_messages = session['button_messages']
        
        # Get the name of the clicked button and update its state
        button_name = request.form.get('button_name')
        button_states[button_name] = True
        
        # Retrieve the message associated with the clicked button
        message = button_messages.get(button_name)
        
        # Generate a response based on the user's input and the previous message history
        reply_content, message_history = prompt(message, message_history)
    
        # Extract the story text and options from the generated response
        text = reply_content.split('Option 1')[0]
        options = re.findall('Option \d:.*', reply_content)
        
        # Update the button messages and states with the new options
        button_messages = {}
        for i, option in enumerate(options):
            button_messages[f'button{i+1}'] = option
            
        for button_name in button_messages.keys():
            button_states[button_name] = False

    # Store the updated variables in the session
    session['message_history'] = message_history
    session['button_messages'] = button_messages

    # Get an image based on the current story text
    image_url = get_img(text+', make it in ghibli studio style, wide-angle perspective')

    # Render the HTML template with the updated variables
    return render_template('index.html', title=title, text=text,
                image_url=image_url, button_messages=button_messages,button_states=button_states, message=message)
    
    
if __name__ == "__main__":
    app.run(debug=True, port=5001)