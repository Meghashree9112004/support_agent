# AI Support Assistant & Ticket Resolver Agent

**Category:** Category 3 — Sales, Marketing & Support  
**Agent Type:** Support Assistant

## Overview
AI Support Assistant is a lightweight support chat application that answers frequently asked questions from a knowledge base and automatically converts unresolved queries into support tickets. The app includes a user-friendly pink-themed chat UI, autocomplete suggestions, and an admin dashboard to view and close tickets.

## Features
- FAQ answering using `faqs.json` (fast local matching)
- Autocomplete suggestions while typing ( `/suggest` )
- GPT / external model fallback (optional)
- Automatic ticket creation for unresolved queries
- Admin dashboard to view and close tickets
- Chat transcript download (optional)
- Simple SQLite storage (`database.db`)

## Tech Stack & APIs
- Backend: Python + Flask
- Frontend: HTML + CSS + JS (templates in `templates/`)
- Database: SQLite (`database.db`)
- Hosting: Render / Railway / Heroku (recommended)
- Optional: OpenAI / other LLMs for fallback answers

## Project Structure
