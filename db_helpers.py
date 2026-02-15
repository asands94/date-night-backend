import os
import psycopg2


def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return connection


def consolidate_completed_dates_in_date_ideas(date_ideas_with_completed_dates):
    consolidated_date_ideas = []
    for date_idea in date_ideas_with_completed_dates:
        date_idea_exists = False
        for consolidated_date_idea in consolidated_date_ideas:
            if date_idea["id"] == consolidated_date_idea["id"]:
                date_idea_exists = True
                consolidated_date_idea["completed_dates"].append(
                    {"completed_date_text": date_idea["completed_date_text"],
                     "completed_date_id": date_idea["completed_date_id"],
                     "completed_date_date": date_idea["completed_date_date"],
                     "completed_date_opinion": date_idea["completed_date_opinion"],
                     "completed_date_image_url": date_idea["completed_date_image_url"],
                     "completed_date_author_username": date_idea["completed_date_author_username"]
                     })
                break

        if not date_idea_exists:
            date_idea["completed_dates"] = []
            if date_idea["completed_date_id"] is not None:
                date_idea["completed_dates"].append(
                    {"completed_date_text": date_idea["completed_date_text"],
                     "completed_date_id": date_idea["completed_date_id"],
                     "completed_date_date": date_idea["completed_date_date"],
                     "completed_date_opinion": date_idea["completed_date_opinion"],
                     "completed_date_image_url": date_idea["completed_date_image_url"],
                     "completed_date_author_username": date_idea["completed_date_author_username"]
                     }
                )
            del date_idea["completed_date_id"]
            del date_idea["completed_date_text"]
            del date_idea["completed_date_author_username"]
            del date_idea["completed_date_date"]
            del date_idea["completed_date_opinion"]
            del date_idea["completed_date_image_url"]
            consolidated_date_ideas.append(date_idea)

    return consolidated_date_ideas
