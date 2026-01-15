# Redis Best Practices — Examples

This project contains a set of best-practice examples implemented with Redis. For details, please refer to the `README.md` file inside each example.

## chatbot
A ChatBot system enhanced with Redis Vector Similarity Search. It vectorizes and stores users' conversation history, retrieves semantically similar past conversations when answering questions, and generates more accurate replies by combining retrieved context with the current query.

## sso_login
A Redis-based Single Sign-On (SSO) login system. It stores user login/session information in Redis to enable SSO across multiple services.