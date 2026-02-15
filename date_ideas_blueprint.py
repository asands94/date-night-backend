from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from db_helpers import get_db_connection

date_ideas_blueprint = Blueprint('date_ideas_blueprint', __name__)


@date_ideas_blueprint.route('/date-ideas', methods=['POST'])
@token_required
def create_date_idea():
    try:
        author_id = g.user["id"]

        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")

        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO date_ideas (author, name, description, category)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """,
                       (author_id, name, description, category)
                       )
        date_idea_id = cursor.fetchone()["id"]
        cursor.execute("""SELECT d.id,
                            d.author AS hoot_author_id,
                            d.name,
                            d.description,
                            d.category,
                            u_date_idea.username AS author_username
                        FROM date_ideas d
                        JOIN users u_date_idea ON d.author = u_date_idea.id
                        WHERE d.id = %s
                       """, (date_idea_id,))
        created_date_idea = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(created_date_idea), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
