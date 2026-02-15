from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from db_helpers import get_db_connection, consolidate_completed_dates_in_date_ideas

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
                            d.author AS date_idea_author_id,
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


@date_ideas_blueprint.route('/date-ideas/<date_idea_id>', methods=['PUT'])
@token_required
def update_date_idea(date_idea_id):
    try:

        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")

        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM date_ideas WHERE date_ideas.id = %s", (date_idea_id,))
        date_idea_to_update = cursor.fetchone()
        if date_idea_to_update is None:
            return jsonify({"error": "date idea not found"}), 404
        connection.commit()
        if date_idea_to_update["author"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute("UPDATE date_ideas SET name = %s, description = %s, category = %s WHERE date_ideas.id = %s RETURNING *",
                       (name, description, category, date_idea_id))
        date_idea_id = cursor.fetchone()["id"]
        cursor.execute("""SELECT d.id, 
                            d.author AS date_idea_author_id, 
                            d.name, 
                            d.description, 
                            d.category, 
                            u_date_idea.username AS author_username
                        FROM date_ideas d
                        JOIN users u_date_idea ON d.author = u_date_idea.id
                        WHERE d.id = %s
                       """, (date_idea_id,))
        updated_date_idea = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(updated_date_idea), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@date_ideas_blueprint.route('/date-ideas', methods=['GET'])
def date_ideas_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""SELECT d.id, 
                            d.author AS date_idea_author_id, 
                            d.name, 
                            d.description, 
                            d.category, 
                            u_date_idea.username AS author_username
                        FROM date_ideas d
                        JOIN users u_date_idea ON d.author = u_date_idea.id
                       """,)
        date_ideas = cursor.fetchall()

        connection.commit()
        connection.close()
        return jsonify(date_ideas), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@date_ideas_blueprint.route('/date-ideas/<date_idea_id>', methods=['GET'])
def date_idea_show(date_idea_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""SELECT d.id, 
                            d.author AS date_idea_author_id, 
                            d.name, 
                            d.description, 
                            d.category,
                            u_date_idea.username AS author_username, 
                            c.id AS completed_date_id, 
                            c.text AS completed_date_text,
                            c.opinion AS completed_date_opinion,
                            c.image_url AS completed_date_image_url,   
                            c.date AS completed_date_date, 
                            u_completed_date.username AS completed_date_author_username
                        FROM date_ideas d
                        INNER JOIN users u_date_idea ON d.author = u_date_idea.id
                        LEFT JOIN completed_dates c ON d.id = c.idea
                        LEFT JOIN users u_completed_date ON c.author = u_completed_date.id
                        WHERE d.id = %s;
                        """,
                       (date_idea_id,))
        unprocessed_date_idea = cursor.fetchall()
        if unprocessed_date_idea is not None:
            processed_date_idea = consolidate_completed_dates_in_date_ideas(unprocessed_date_idea)[
                0]
            connection.close()
            return jsonify(processed_date_idea), 200
        else:
            connection.close()
            return jsonify({"error": "Date idea not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@date_ideas_blueprint.route('/date-ideas/<date_idea_id>', methods=['DELETE'])
@token_required
def delete_date_idea(date_idea_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM date_ideas WHERE date_ideas.id = %s", (date_idea_id,))
        date_idea_to_delete = cursor.fetchone()
        if date_idea_to_delete is None:
            return jsonify({"error": "Date idea not found"}), 404
        connection.commit()
        if date_idea_to_delete["author"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute(
            "DELETE FROM date_ideas WHERE date_ideas.id = %s", (date_idea_id,))
        connection.commit()
        connection.close()
        return jsonify(date_idea_to_delete), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
