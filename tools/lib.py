# tool_lib.py

import os


def get_lib():
    lib = """
Websites:
    Vercel's homepage. Vercel is a serverless function host platform, the arXiv sentinel should be deploy to this platform:
    https://vercel.com/ 
    
    Google APP password page. arXiv sentinel needs to send emails to users, so it needs to get the APP password from this website:
    https://myaccount.google.com/apppasswords
    
    OpenAI API key page. arXiv sentinel needs to use LLM to summarize papers, so you need to get the key from this website:
    https://platform.openai.com/settings/profile

    Arxiv homepage:
    https://arxiv.org/

CLI Tools:
    Local test vercel project:
    vercel dev
    
    Deploy vercel project:
    vercel deploy --prod

    Add env variables in vercel:
    echo [value] | vercel env add [name] [environment]
    environment can be: production | development
    
    Remove env variables in vercel:
    vercel env rm [name]
    
    Get Existing env variables (you will get a file '.env.local'):
    vercel env pull

    """

    return lib
