import time
from datetime import datetime
import sqlalchemy as sa

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import scoped_session, object_session, backref
from sqlalchemy_utils import EmailType, PasswordType, force_auto_coercion, PhoneNumberType
from werkzeug.security import generate_password_hash, check_password_hash

force_auto_coercion()

db = SQLAlchemy()


def obj_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


class User(db.Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    firstname = sa.Column(sa.String, nullable=False)
    lastname = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=True, default=None)
    phone = sa.Column(sa.String, nullable=True, default=None)
    is_admin = sa.Column(sa.Boolean, nullable=False, default=False)
    password = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))


class Property(db.Model):
    __tablename__ = "property"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    area = sa.Column(sa.Integer, nullable=False)
    bedroom = sa.Column(sa.Integer, nullable=False)
    parking = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))
    star = sa.Column(sa.Boolean, nullable=False, default=False)
    locality = sa.Column(sa.String, nullable=False)
    lat = sa.Column(sa.Float, nullable=True)
    long = sa.Column(sa.Float, nullable=True)
    images_count = sa.Column(sa.Integer, nullable=False, default=0)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    comments = sa.orm.relationship(
        "Comment",
        cascade="all, delete-orphan",
        back_populates="prop",
        primaryjoin='Property.id==Comment.property_id'
    )
    pics = sa.orm.relationship(
        "PropertyPic",
        cascade="all, delete-orphan",
        back_populates="prop",
        primaryjoin='Property.id==PropertyPic.property_id'
    )
    # bookmarked = sa.orm.relationship(
    #     "Bookmarked",
    #     cascade="all, delete-orphan",
    #     back_populates="props",
    #     secondary="Bookmarked"
    #     # primaryjoin='Property.id==Bookmarked.property_id'
    # )

    @hybrid_property
    def location(self):
        doc = {
            "locality": self.locality,
            "lat": self.lat,
            "long": self.long,
        }

        return doc

    @hybrid_property
    def breadcrumb(self):
        return ['خرید', 'شهر تهران', self.locality]

    @hybrid_property
    def comments_pretty(self):
        res = []
        for c in self.comments:
            res.append(obj_to_dict(c))

        return res

    @hybrid_property
    def pics_pretty(self):
        res = []
        for c in self.pics:
            res.append(obj_to_dict(c))

        return res


class Comment(db.Model):
    __tablename__ = "comment"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    comment = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))

    # user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    property_id = sa.Column(sa.Integer, sa.ForeignKey("property.id"), nullable=False)

    prop = sa.orm.relationship(
        "Property",
        # foreign_keys=property_id,
        back_populates="comments",
        uselist=False,
        lazy=False
    )


class Bookmarked(db.Model):
    __tablename__ = "bookmarked"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    property_id = sa.Column(sa.Integer, sa.ForeignKey("property.id"), nullable=False)

    # props = sa.orm.relationship(
    #     "Property",
    #     foreign_keys=property_id,
    #     back_populates="bookmarked",
    #     # cascade="all, delete-orphan",
    # )


class PropertyPic(db.Model):
    __tablename__ = "property_pic"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    path = sa.Column(sa.String, nullable=False)

    property_id = sa.Column(sa.Integer, sa.ForeignKey("property.id"), nullable=False)

    prop = sa.orm.relationship(
        "Property",
        # foreign_keys=property_id,
        back_populates="pics",
        uselist=False,
        lazy=False
    )
