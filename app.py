import json
import os

from werkzeug.utils import secure_filename

from models import *
import flask
from flask_cors import CORS, cross_origin
from flasgger import Swagger, swag_from
from flask import Flask, render_template, request, jsonify, redirect, session, make_response
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
import hashlib

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Access-Control-Allow-Methods: *"
app.config["SECRET_KEY"] = 'parsa9531908'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:7410@localhost/kilid'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["BASE_UPLOAD_FOLDER"] = os.path.join('E:\\Development\\WP\\9531908_HW3\\src', "assets")
app.config["SWAGGER"] = {
    # "swagger_version": "3.20.9",
    "specs": [
        {"version": "1.0", "title": "KILID API", "endpoint": "api", "route": "/api"}
    ]
}

Swagger(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
dbsession = (sessionmaker(bind=engine))
mysession = dbsession()

db.init_app(app)
migrate = Migrate(app, db)

PICS_NO = 0
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def validate_password(user, password):
    # hash_pass = hashlib.md5(password.encode()).hexdigest()
    return user.password == password


def allowed_image(filename):
    if (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong image format')


def add_pic(_session, prop, pic):
    document = {
        "property_id": prop.id,
        "path": pic
    }

    image = PropertyPic(**document)
    _session.add(image)

    prop.images_count += 1
    _session.commit()


@app.route("/api/test", methods=["GET"])
def test():
    pass


@app.route("/api/register", methods=["POST"])
@cross_origin()
@swag_from("docs/register.yml")
def register():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        mail_phone = request.json.get("mail_phone").lower()
        password = hashlib.md5(
            request.json.get("password").encode()
        ).hexdigest()

        document = {'firstname': firstname, 'lastname': lastname, 'password': password}

        dbemail = mysession.query(User)
        if '@' in mail_phone:
            document['email'] = mail_phone
            dbemail = dbemail.filter_by(email=document['email']).first()
        else:
            document['phone'] = mail_phone
            dbemail = dbemail.filter_by(phone=document['phone']).first()

        # check if the email already exists
        if dbemail:
            resp = make_response(jsonify({'error': "email or phone already exists!", 'status': 401}), 401)
            return resp

        # insert
        user = User(**document)  # unpack the document
        mysession.add(user)
        mysession.commit()

        resp = make_response(jsonify({
            'msg': "You are registered!",
            'token': str(user.id) + '-' + str(user.is_admin),
            'user': obj_to_dict(user),
            'status': 200
        }), 200)

        mysession.close()

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/login", methods=["POST"])
@cross_origin()
@swag_from("docs/login.yml")
def login():
    resp = make_response(jsonify({'error': 'fatal error!', 'status': 500}), 500)

    try:
        is_email = True

        if "email_phone" in request.json.keys():
            email_phone = request.json.get("email_phone")
            if '@' in request.json:
                email_phone = email_phone.lower()
            else:
                is_email = False
        else:
            resp = make_response(jsonify({'error': "Email or phone is needed!", 'status': 401}), 401)
            return resp

        if "password" in request.json.keys():
            password = hashlib.md5(
                request.json.get("password").encode()
            ).hexdigest()
        else:
            resp = make_response(jsonify({'error': "Password is needed!", 'status': 401}), 401)
            return resp

        user = mysession.query(User)
        user = user.filter_by(email=email_phone) if is_email else user.filter_by(phone=email_phone)
        user = user.filter_by(password=password).first()

        if user is None:
            resp = make_response(jsonify({'error': "Wrong info!", 'status': 500}), 500)
            return resp

        if user is not None and validate_password(user, password):
            document = {
                'msg': "You are logged in!",
                'token': str(user.id) + '-' + str(user.is_admin),
                'user': obj_to_dict(user),
                'status': 200
            }
            resp = make_response(jsonify(document), 200)

        return resp

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/logout", methods=["POST"])
@cross_origin()
@swag_from("docs/logout.yml")
def logout():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        user_id = int(request.json.get('user_id'))
        user = mysession.query(User).filter_by(id=user_id).first()

        doc = {
            'msg': 'Logged out successfully!',
            'token': str(user.id) + '-' + str(user.is_admin),
            'user': obj_to_dict(user),
            'status': 200
        }

        resp = make_response(jsonify(doc), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/promote", methods=["PUT"])
@cross_origin()
@swag_from("docs/promote.yml")
def promote():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        user_id = int(request.json.get('user_id'))
        user = mysession.query(User).filter_by(id=user_id).first()

        user.is_admin = True

        mysession.commit()

        doc = {
            'msg': 'user promoted to admin successfully!',
            'token': str(user.id) + '-' + str(user.is_admin),
            'user': obj_to_dict(user),
            'status': 200
        }

        resp = make_response(jsonify(doc), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/user/<user_id>", methods=["PUT", "GET", "DELETE"])
@cross_origin()
@swag_from("docs/edit.yml")
def edit(user_id):
    resp = make_response(jsonify({'error': 'fatal error!', 'status': 500}), 500)

    try:
        user_id = int(user_id)
        user = mysession.query(User).filter_by(id=user_id)

        if flask.request.method == "PUT":
            user = user.first()

            if "email" in request.json.keys() and request.json["email"] is not None:
                user.email = request.json["email"].lower()

            if "phone" in request.json.keys() and request.json["phone"] is not None:
                user.phone = request.json["phone"]

            if "password" in request.json.keys() and request.json["password"] is not None:
                user.password = hashlib.md5(
                    request.json["password"].encode()
                ).hexdigest()

            if "firstname" in request.json.keys() and request.json["firstname"] is not None:
                user.firstname = request.json["firstname"]

            if "lastname" in request.json.keys() and request.json["lastname"] is not None:
                user.lastname = request.json["lastname"]

            resp = make_response(jsonify({'msg': "user information edited successfully!", 'status': 200}), 200)
            mysession.commit()

        elif flask.request.method == "DELETE":
            props = mysession.query(Bookmarked).filter_by(user_id=user_id)
            ids = [p.id for p in props]

            for property_id in ids:
                mysession.query(Bookmarked).filter_by(property_id=property_id).delete()
                mysession.query(Comment).filter_by(property_id=property_id).delete()
                mysession.query(PropertyPic).filter_by(property_id=property_id).delete()
                mysession.query(Property).filter_by(id=property_id).delete()

            user.delete()
            resp = make_response(jsonify({'msg': "user deleted successfully!", 'status': 200}), 200)
            mysession.commit()

        elif flask.request.method == "GET":
            user = user.first()
            document = obj_to_dict(user)
            document['status'] = 200
            resp = make_response(jsonify(document), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/user/all", methods=["GET"])
@cross_origin()
@swag_from("docs/all.yml")
def all_users():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        users = mysession.query(User)

        res = []
        for user in users:
            res.append(obj_to_dict(user))

        document = {'all': res, 'status': 200}
        resp = make_response(jsonify(document), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/<property_id>", methods=["PUT", "GET", "DELETE"])
@cross_origin()
@swag_from("docs/property.yml")
def property_utils(property_id):
    resp = make_response(jsonify({'error': 'fatal error!', 'status': 500}), 500)

    try:
        property_id = int(property_id)
        prop = mysession.query(Property).filter_by(id=property_id)

        if flask.request.method == "PUT":
            prop = prop.first()

            if "title" in request.json.keys():
                prop.title = request.json["title"]

            if "type" in request.json.keys():
                prop.type = request.json["type"]

            if "price" in request.json.keys():
                prop.price = int(request.json["price"])

            if "area" in request.json.keys():
                prop.area = int(request.json["area"])

            if "bedroom" in request.json.keys():
                prop.bedroom = int(request.json["bedroom"])

            if "parking" in request.json.keys():
                prop.parking = int(request.json["parking"])

            if "locality" in request.json.keys():
                prop.locality = request.json["locality"]

            if "lat" in request.json.keys():
                prop.lat = float(request.json["lat"])

            if "long" in request.json.keys():
                prop.long = float(request.json["long"])

            if "pic" in request.files.keys():
                file = request.files.get('pic')

                if file.filename == '':
                    resp = make_response(jsonify({'error': 'EMPTY FILE!', 'status': 401}), 401)
                    mysession.close()
                    return resp

                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(app.config["BASE_UPLOAD_FOLDER"], str(property_id))
                    path = os.path.join(temp_path, filename)
                    add_pic(mysession, prop, path)
                    file.save(path)

            resp = make_response(jsonify({'msg': "Property information edited successfully!", 'status': 200}), 200)
            mysession.commit()

        elif flask.request.method == "DELETE":
            mysession.query(Bookmarked).filter_by(property_id=property_id).delete()
            mysession.query(Comment).filter_by(property_id=property_id).delete()
            mysession.query(PropertyPic).filter_by(property_id=property_id).delete()
            prop.delete()
            resp = make_response(jsonify({'msg': "Property deleted successfully!", 'status': 200}), 200)
            mysession.commit()

        elif flask.request.method == "GET":
            prop = prop.first()
            document = obj_to_dict(prop)
            # document['status'] = 200

            document['pics'] = prop.pics_pretty
            document['comments'] = prop.comments_pretty
            document['breadcrumb'] = prop.breadcrumb

            books = mysession.query(Bookmarked).filter_by(property_id=prop.id)
            uids = [b.user_id for b in books]

            document['bookers'] = uids

            resp = make_response(jsonify(document), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property", methods=["POST", "GET"])
@cross_origin()
@swag_from("docs/properties.yml")
def properties():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        if flask.request.method == "POST":
            in_title = request.json.get("title")
            in_type = request.json.get("type")
            in_price = int(request.json.get("price"))
            in_area = int(request.json.get("area"))
            in_bedroom = int(request.json.get("bedroom"))
            in_parking = int(request.json.get("parking"))
            in_locality = request.json.get("locality")
            in_lat = float(request.json.get("lat"))
            in_long = float(request.json.get("long"))
            user_id = int(request.json.get("user_id"))

            document = {
                "title": in_title,
                "type": in_type,
                "price": in_price,
                "area": in_area,
                "bedroom": in_bedroom,
                "parking": in_parking,
                "locality": in_locality,
                "lat": in_lat,
                "long": in_long,
                "user_id": user_id,
            }

            prop = Property(**document)

            mysession.add(prop)
            mysession.commit()

            new_prop = mysession.query(Property).order_by(Property.id.desc()).first()

            if "pic" in request.files.keys():
                file = request.files.get('pic')

                if file.filename == '':
                    resp = make_response(jsonify({'error': 'EMPTY FILE!', 'status': 401}), 401)
                    mysession.close()
                    return resp

                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(app.config["BASE_UPLOAD_FOLDER"], str(new_prop.id))

                    if not os.path.isdir(temp_path):
                        os.makedirs(temp_path, exist_ok=True)

                    path = os.path.join(temp_path, filename)
                    add_pic(mysession, prop, path)
                    file.save(path)

            mysession.commit()

            resp = make_response(jsonify({'msg': 'Property added successfully!', 'status': 200}), 200)

        elif flask.request.method == "GET":
            props = mysession.query(Property)

            res = []
            for p in props:
                x = obj_to_dict(p)
                x['pics'] = p.pics_pretty
                x['comments'] = p.comments_pretty
                x['breadcrumb'] = p.breadcrumb

                books = mysession.query(Bookmarked).filter_by(property_id=p.id)
                uids = [b.user_id for b in books]

                x['bookers'] = uids

                res.append(x)

            doc = {'all': res, 'status': 200}
            # print(jsonify(dict(doc)))
            resp = make_response(jsonify(doc), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/occasion", methods=["PUT"])
@cross_origin()
@swag_from("docs/occasion.yml")
def occasion():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        property_id = int(request.json.get('property_id'))
        prop = mysession.query(Property).filter_by(id=property_id).first()

        prop.star = True

        mysession.commit()

        resp = make_response(jsonify({'msg': "Property is an occasion now!", 'status': 200}), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/bookmark/<user_id>/<property_id>", methods=["GET"])
@cross_origin()
# @swag_from("docs/bookmark.yml")
def is_bookmark(user_id, property_id):
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        booked = mysession.query(Bookmarked).filter_by(user_id=user_id).filter_by(property_id=property_id).first()

        res = 1 if booked is not None else 0

        resp = make_response(jsonify({'bookmarked': res, 'status': 200}), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/pics/<property_id>", methods=["GET"])
@cross_origin()
# @swag_from("docs/bookmark.yml")
def pics(property_id):
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        pics = mysession.query(PropertyPic).filter_by(property_id=property_id)

        res = []
        for p in pics:
            res.append(obj_to_dict(p))

        resp = make_response(jsonify({'pics': res, 'status': 200}), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/bookmark", methods=["PUT", "DELETE"])
@cross_origin()
@swag_from("docs/bookmark.yml")
def bookmark():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        user_id = int(request.json.get('user_id'))
        property_id = int(request.json.get('property_id'))

        if flask.request.method == "PUT":

            document = {
                "user_id": user_id,
                "property_id": property_id,
            }

            bookmarked = Bookmarked(**document)
            mysession.add(bookmarked)
            mysession.commit()

            resp = make_response(jsonify({'msg': "Property bookmarked successfully!", 'status': 200}), 200)

        elif flask.request.method == "DELETE":
            prop = mysession.query(Bookmarked).filter_by(user_id=user_id).filter_by(property_id=property_id)
            prop.delete()

            mysession.commit()

            resp = make_response(jsonify({'msg': "Bookmark deleted successfully!", 'status': 200}), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/search", methods=["GET"])
@cross_origin()
@swag_from("docs/search.yml")
def search():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        if 'locality' in flask.request.args.keys():
            locality = flask.request.args.get('locality')
        else:
            locality = None

        if 'price_start' in flask.request.args.keys():
            price_start = int(flask.request.args.get('price_start'))
        else:
            price_start = None

        if 'area_start' in flask.request.args.keys():
            area_start = int(flask.request.args.get('area_start'))
        else:
            area_start = None

        if 'price_end' in flask.request.args.keys():
            price_end = int(flask.request.args.get('price_end'))
        else:
            price_end = None

        if 'area_end' in flask.request.args.keys():
            area_end = int(flask.request.args.get('area_end'))
        else:
            area_end = None

        props = mysession.query(Property)

        # simple search
        props = props.filter_by(locality=locality) if locality is not None else props

        # advanced search
        if price_start is not None and price_end is not None:
            props = props.filter(Property.price.between(price_start, price_end))

        if area_start is not None and area_end is not None:
            props = props.filter(Property.area.between(area_start, area_end))

        res = []
        for p in props:
            x = obj_to_dict(p)
            x['pics'] = p.pics_pretty
            x['comments'] = p.comments_pretty
            x['breadcrumb'] = p.breadcrumb

            books = mysession.query(Bookmarked).filter_by(property_id=p.id)
            uids = [b.user_id for b in books]

            x['bookers'] = uids

            res.append(x)

        document = {'result': res, 'status': 200}
        resp = make_response(jsonify(document), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/user/property/<user_id>", methods=["GET"])
@cross_origin()
@swag_from("docs/owner.yml")
def user_properties(user_id):
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        bookmarked = int(flask.request.args.get('bookmark'))

        if bookmarked == 1:
            booked = mysession.query(Bookmarked).filter_by(user_id=user_id)

            ids = []
            for b in booked:
                ids.append(b.property_id)

            props = mysession.query(Property).filter(Property.id.in_(ids))

        else:
            props = mysession.query(Property).filter_by(user_id=user_id)

        res = []
        for p in props:
            x = obj_to_dict(p)
            x['pics'] = p.pics_pretty
            x['comments'] = p.comments_pretty
            x['breadcrumb'] = p.breadcrumb

            books = mysession.query(Bookmarked).filter_by(property_id=p.id)
            uids = [b.user_id for b in books]

            x['bookers'] = uids

            res.append(x)

        document = {'all': res, 'status': 200}
        resp = make_response(jsonify(document), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


@app.route("/api/property/comment", methods=["POST"])
@cross_origin()
@swag_from("docs/comment.yml")
def comment():
    resp = make_response(jsonify({'error': "fatal error!", 'status': 500}), 500)

    try:
        property_id = request.json.get('property_id')
        cm = request.json.get('comment')

        document = {
            'property_id': property_id,
            'comment': cm,
        }

        comment_obj = Comment(**document)
        mysession.add(comment_obj)
        mysession.commit()

        doc = {
            'msg': 'Comment added successfully!',
            'status': 200
        }
        resp = make_response(jsonify(doc), 200)

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        mysession.close()
        return resp


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
