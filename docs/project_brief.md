# The Job Posting Fit Scorer
- currently active project.

## What it does
Takes a job posting + my profile `jane_doe_profile.md` as inputs, extracts required skills from the posting, compares them against your skills, and outputs a fit score with missing skills + a repositioning suggestion. Basically automates the gap analysis I am doing manually.

## Structure: NEGOTIABLE; NEED INPUTS
- OOP structure to be discussed
- An app interface (can be exe, vercel, streamlit,... something else)
- Must be modular and extendable. Say in the fututre if I want to extend it or connect it to a web scraper I must be able to do it

## Methodology in the project: TO BE FOLLOWED
- Test Drvien Development (Write component tests before developing the code)
- If the test fails anlyse the root cause. Whether or not the test needs to be changed or it is a bug is decision that **has to be signed off by a human**
- Final system integration testing and user acceptance testing to be done using some sort of GUi test tool (OPTIONAL)

## Stack
- Ollama for iterative dev, Gemini API for final testing. (NON NEGOTIABLE)
- Langchain (NON NEGOTIABLE)
- Python (NON NEGOTIABLE)
- GUI (choice depends on decision in point 2 of structure) (NEED INPUT)
- Testing - pytest and Playwright(?) (NEED INPUT)

## Security must haves: NEED INPUTS
- Data to be protected. Think along the lines of not sending ANY personal data to the LLM (insititute names, personal data)
- Protection against injection attacks

