## ChatBot Powered by Redis Vector Similarity Search

### Overview
This is a ChatBot system enhanced with Redis Vector Similarity Search. It vectorizes and stores users' conversation history. When answering questions, it retrieves relevant historical conversations based on semantic similarity, and generates more accurate replies by combining the retrieved context with the current input.

### Workflow
1. The user enters a question or message.
2. The system converts the user input into a vector representation.
3. The system performs a vector similarity search in Redis and retrieves the most relevant historical conversations.
4. The system combines the retrieved historical conversations with the current user input to generate a more accurate reply.

### Notes
- This system is for demonstration purposes only. It is not intended for commercial use and comes with no warranty.

### License
MIT License