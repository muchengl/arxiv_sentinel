# arXiv Sentinel 🤖
This is an LLM Agent system, which can be deployed in a [Vercel](https://vercel.com/) serverless function. 
Contains the following functions:
- Scan arXiv by configuration
- Summarizes new papers by LLM
- Send you a paper report via email


Let our LLM assistant help you automatically configure this bot!
```shell
python assistant.py
```

## Manual Configuration
Prerequisite:
```shell
# Vercel Account:
https://vercel.com

# Install vercel cli tool
https://vercel.com/docs/cli

# Google App password
https://myaccount.google.com/apppasswords

# OpenAI API Key
https://platform.openai.com/settings/profile?tab=api-keys

# arXiv topic (e.g. cs.AI)
https://arxiv.org/

```

Env var setup:
```shell
vercel env add
# EMAIL_ADDRESS="your_email_address@gmail.com"
# EMAIL_PASSWORD="your_google_app_password"
# OPENAI_API_KEY="your_opanai_API_key"
# PAPER_TOPIC="arXiv_topic"
# TARGET_ADDRESS="email_address_to_get_report "

```

Deploy to Vercel:
```shell
 vercel deploy --prod
```

Test Locally:
```shell
vercel dev

curl http://localhost:3000/api/cron/job
```

