# arXiv Sentinel 🤖
This is an LLM Agent system, which can be deployed in a [Vercel](https://vercel.com/) serverless function. 
- Scan arXiv
- Summarizes papers by LLM
- Send you report emails


Lets our LLM assistant help you automatically configure this bot!
```shell
python assistant.py
```

## Manual Configuration
Prerequisite:
```shell
# Google App password
https://myaccount.google.com/apppasswords

# Vercel Account:
https://vercel.com

# OpenAI API Key
https://platform.openai.com/settings/profile?tab=api-keys

# arXiv topic
https://arxiv.org/

```

Deploy:
```shell
 vercel deploy --prod
```

Test Locally:
```shell
vercel dev

curl http://localhost:3000/api/cron/job
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