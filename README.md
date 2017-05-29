# What Would They Say?

A Markov-Chain generating slackbot for when your coworker moves to Ireland and
you have to find a way to ask them questions despite the time difference.

## Getting Started

### Getting a Slack Token

1. [Create a new slack app](https://api.slack.com/apps)
2. Add the `channels:history` and `channels:read` permission scopes under
   `OAuth and Permissions`.

### Configure a `.env` file

You'll need to create a `.env` file, based off of `.env-template`. Pick some
secure values for the mysql passwords and input your slack token.

### Ingest some data

In order to actually respond with any messages, you need to crawl the slack
history and get a user's past messages:

```bash
docker-compose -f docker-compose.yaml -f docker-compose.yaml.scripts run -e LOAD_USERNAME={their_slack_username} ingest-user
```

### Run The Bot

Once you've ingested some data, run the mysql database and the main slack
listener with the following:
```bash
docker-compose -f docker-compose.yaml up -d
```

### One-Off Messages

You can also do a one-off message generator:

```bash
docker-compose -f docker-compose.yaml -f docker-compose.yaml.scripts run -e LOAD_USERNAME={their_slack_username} wwts
```
