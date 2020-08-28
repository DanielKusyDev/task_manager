import json


class SlackMessage:

    @staticmethod
    def get_header(content):
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": content
            }
        }

    @staticmethod
    def get_field_section(fields_content):
        fields = [{"type": "mrkdwn", "text": content} for content in fields_content]
        section = {
            "type": "section",
            "fields": fields
        }
        return section

    @staticmethod
    def get_text_section(content):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": content
            }
        }

    @staticmethod
    def get_divider():
        return {"type": "divider"}


def get_new_task_slack_message(description, end_date):
    slack_message = SlackMessage
    fields = [
        f"*Task*: {description}",
        f"*End date*: {end_date}"
    ]
    message = {
        "blocks": [
            slack_message.get_header("New task scheduled!"),
            slack_message.get_divider(),
            slack_message.get_field_section(fields)
        ]
    }
    return json.dumps(message)


def get_slack_reminder_message(description, end_date):
    slack_message = SlackMessage()

    main_content = f"The planned deadline for the task is nearing its end :clock2: Make sure to finish it on time."
    fields = [
        f"*Task*: {description}",
        f"*End date*: {end_date}"
    ]
    message = {
        "blocks": [
            slack_message.get_header("Finish the task on time!"),
            slack_message.get_divider(),
            slack_message.get_text_section(main_content),
            slack_message.get_divider(),
            slack_message.get_field_section(fields)
        ]
    }
    return json.dumps(message)
