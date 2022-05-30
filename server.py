from flask import Flask, render_template, request, redirect, url_for
from database import query

from math import ceil

app = Flask(__name__)


@app.get("/")
@app.get("/page/<int:page_number>/")
def index(page_number=0):
    total_pages = query("SELECT count(id) FROM shows", single=True)
    total_pages = int(total_pages["count"]) / 30
    total_pages = ceil(total_pages)

    shows = query(
        """
            SELECT
                id, title, rating
            FROM
                shows
            LIMIT %(count)s
            OFFSET %(page_number)s;
        """,
        {
            "page_number": page_number * 30,
            "count": 30,
        },
    )
    return render_template(
        "index.html",
        shows=shows,
        pages=total_pages,
    )


@app.get("/show/<int:id>/")
def show(id):
    the_show = query(
        """
        SELECT title, overview, rating
        FROM shows
        WHERE id = %(show_id)s;
    """,
        {"show_id": id},
        single=True,
        debug=True,
    )

    return render_template(
        "show.html",
        title=the_show["title"],
        overview=the_show["overview"],
        rating=the_show["rating"],
        id=id,
    )


@app.get("/genres/")
def genres():
    gs = query("SELECT id, name FROM genres;")
    return render_template("genres.html", genres=gs)


@app.get("/genre/<int:id>")
@app.get("/genre/<int:id>/")
def genre(id):
    shows = query(
        """
        SELECT
            s.id, s.title
        FROM shows s

        LEFT JOIN
            show_genres sg
        ON sg.show_id = s.id
        
        LEFT JOIN
            genres g
        ON g.id = sg.genre_id

        WHERE
            g.id = %(gid)s;
    """,
        {"gid": id},
        debug=True,
    )
    return render_template("index.html", shows=shows)


@app.get("/add")
def add_form():
    return render_template("add_form.html")


@app.post("/add")
def add_show():
    title = request.form.get("title")
    rating = request.form.get("rating")
    overview = request.form.get("overview")

    new_id = query(
        """
            SELECT
                count(id) AS total
            FROM shows;
        """,
        single=True,
    )
    new_id = int(new_id["total"]) + 1

    generated_id = query(
        """
            INSERT INTO shows
            (id, title, rating, overview)
            VALUES (%(new_id)s, %(title)s, %(rating)s, %(overview)s)
            RETURNING id;
        """,
        {
            "new_id": new_id,
            "title": title,
            "rating": rating,
            "overview": overview,
        },
        single=True,
    )

    return redirect(
        url_for(
            "show",
            id=generated_id["id"],
        )
    )


@app.get("/edit/<int:id>")
@app.get("/edit/<int:id>/")
def edit_form(id):
    the_show = query(
        """
        SELECT title, overview, rating
        FROM shows
        WHERE id = %(show_id)s;
    """,
        {"show_id": id},
        single=True,
        debug=True,
    )

    return render_template(
        "edit_form.html",
        title=the_show["title"],
        overview=the_show["overview"],
        rating=the_show["rating"],
        id=id,
    )


@app.post("/edit/<int:id>/")
def edit_show(id):
    title = request.form.get("title")
    rating = request.form.get("rating")
    overview = request.form.get("overview")

    generated_id = query(
        """
            UPDATE
                shows
            SET
                title = %(title)s,
                rating = %(rating)s,
                overview = %(overview)s
            WHERE
                id = %(id)s
            RETURNING id;
        """,
        {"title": title, "rating": rating, "overview": overview, "id": id},
        single=True,
        debug=True,
    )

    return redirect(
        url_for(
            "show",
            id=generated_id["id"],
        )
    )


@app.get("/delete/<int:id>")
@app.get("/delete/<int:id>/")
def delete(id):
    _ = query(
        """
        DELETE FROM
            shows
        WHERE
            id = %(id)s
        RETURNING id;
        """,
        {"id": id},
    )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
