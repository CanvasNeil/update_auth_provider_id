import json
import requests


def success_alert(SUCCESS_HOOK, runtime, UPDATED_USER_LOGINS, summary_file, logfile):
    content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Null Auth Provider ID Fix",
                                "fontType": "Default",
                                "size": "Large",
                                "spacing": "None",
                                "wrap": True,
                                "weight": "Bolder",
                                "color": "Good"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": 2,
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "✨ Authentication providers updated successfully",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f"⏱️ Runtime: {runtime:.2f} sec",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f"✔️ Logins udpated: {UPDATED_USER_LOGINS}",
                                "wrap": True
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.OpenUrl",
                                                        "title": "View Summary",
                                                        "style": "positive",
                                                        "url": f"{summary_file}"
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.OpenUrl",
                                                        "title": "View Log",
                                                        "style": "positive",
                                                        "url": f"{logfile}"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "style": "default",
                "separator": True
            }
        ]
    }
    payload = json.dumps(
        {
            'type': 'message',
            'attachments': [
                {
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'contentUrl': 'null',
                    'content': content,
                }
            ]
        }
    )

    headers = {'Content-Type': 'application/json'}
    response = requests.post(SUCCESS_HOOK, headers=headers, data=payload)


def error_alert(ERROR_HOOK, runtime, summary_file, logfile):
    content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Null Auth Provider ID Fix",
                                "fontType": "Default",
                                "size": "Large",
                                "spacing": "None",
                                "wrap": True,
                                "weight": "Bolder",
                                "color": "Warning"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": 2,
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": f"⚠️ Authentication provider update failed",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f"⏱️ Runtime: {runtime:.2f} sec",
                                "wrap": True
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.OpenUrl",
                                                        "title": "View Summary",
                                                        "style": "positive",
                                                        "url": f"{summary_file}"
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.OpenUrl",
                                                        "title": "View Log",
                                                        "style": "positive",
                                                        "url": f"{logfile}"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "style": "default",
                "separator": True
            }
        ]
    }
    payload = json.dumps(
        {
            'type': 'message',
            'attachments': [
                {
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'contentUrl': 'null',
                    'content': content,
                }
            ]
        }
    )

    headers = {'Content-Type': 'application/json'}
    response = requests.post(ERROR_HOOK, headers=headers, data=payload)