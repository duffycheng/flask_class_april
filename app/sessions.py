# sessions.py
import _pickle as pickle
from uuid import uuid4
from datetime import datetime
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from .models import Session
from itsdangerous import want_bytes

class SqliteSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False

class SqliteSessionInterface(SessionInterface):
    serializer = pickle
    session_class = SqliteSession

    def __init__(self, db):
        self.db = db

    def generate_sid(self):
        return str(uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid)
        
        data = Session.query.filter_by(sid=sid).first()
        if data and data.expiry and data.expiry <= datetime.utcnow():
            # Delete expired session
            self.db.session.delete(data)
            self.db.session.commit()
            data = None
        if data is not None:
            val = self.serializer.loads(want_bytes(data.value))
            return self.session_class(val, sid=sid)
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        store_id = session.sid
        saved_session = Session.query.filter_by(
            sid=store_id).first()
        if not session:
            if session.modified:
                    if saved_session:
                        self.db.session.delete(saved_session)
                        self.db.session.commit()
                    response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
            return
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        value = self.serializer.dumps(dict(session))
        if saved_session:
            saved_session.value = value
            saved_session.expiry = expires
            self.db.session.commit()
        else:
            new_session = Session(session.sid, value, expires)
            self.db.session.add(new_session)
            self.db.session.commit()
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=expires, domain=domain,secure=secure)