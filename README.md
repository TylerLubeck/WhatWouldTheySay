# What Would They Say?

A Markov-Chain generating slackbot for when your coworker moves to Ireland and
you have to find a way to ask them questions despite the time difference.

## Getting Started

You'll need to create a `.env` file, based off of `.env-template`. Pick some
secure values for the mysql passwords and get a slack token [by creating a new
slack bot](https://api.slack.com/apps).

Once you've done that, run the mysql database and the main slack listener with
the following:
```bash
docker-compose -f docker-compose.yaml up -d
```

In order to actually respond with any messages, you need to crawl the slack
history and get a user's past messages:

```bash
docker-compose -f docker-compose.yaml -f docker-compose.yaml.scripts run -e LOAD_USERNAME={their_slack_username} ingest-user
```

You can also do a one-off message generator:

```bash
docker-compose -f docker-compose.yaml -f docker-compose.yaml.scripts run -e LOAD_USERNAME={their_slack_username} wwts
```
