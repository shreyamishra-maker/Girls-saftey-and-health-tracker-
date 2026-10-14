import os,tempfile
import pytest
from app import create_app,db
@pytest.fixture()
def app():
 fd,path=tempfile.mkstemp(suffix=".sqlite3");os.close(fd)
 a=create_app({"TESTING":True,"SECRET_KEY":"test-only-secret","WTF_CSRF_ENABLED":False,"SQLALCHEMY_DATABASE_URI":"sqlite:///"+path,"RATELIMIT_ENABLED":False,"SESSION_COOKIE_SECURE":False})
 yield a
 with a.app_context():db.session.remove();db.drop_all()
 os.unlink(path)
@pytest.fixture()
def client(app):return app.test_client()
def register(c,email="person@example.com",pw="test-password-123"):
 return c.post("/register",data={"name":"Test Person","age":"22","email":email,"password":pw,"blood_group":"O+"},follow_redirects=True)
def login(c):return c.post("/login",data={"email":"person@example.com","password":"test-password-123"},follow_redirects=True)
def test_healthz(client):
 r=client.get("/healthz");assert r.status_code==200 and r.json=={"status":"ok"}
def test_register_login_dashboard(client):
 assert b"Account created" in register(client).data
 assert b"Hello, Test Person" in login(client).data
def test_password_and_duplicate_email(client):
 r=client.post("/register",data={"name":"A","email":"short@example.com","password":"tiny"});assert r.status_code==400
 register(client);r=client.post("/register",data={"name":"Other","email":"person@example.com","password":"another-password-456"});assert r.status_code==409
def test_private_dashboard(client):
 assert client.get("/dashboard").status_code==302
def test_core_features(client):
 register(client);login(client)
 assert b"Trusted Friend" in client.post("/contacts",data={"name":"Trusted Friend","phone":"+911234567890","relation":"Friend"},follow_redirects=True).data
 assert b"Period log saved" in client.post("/cycles",data={"start_date":"2026-10-01","end_date":"2026-10-05","cycle_length":"28"},follow_redirects=True).data
 assert b"Symptom log saved" in client.post("/symptoms",data={"log_date":"2026-10-10","headache":"on","mood":"Happy"},follow_redirects=True).data
 client.post("/notes",data={"title":"Doctor questions","content":"Ask about cramps"},follow_redirects=True)
 client.post("/reminders",data={"reminder_type":"Health checkup","message":"Book appointment","remind_date":"2026-11-01"},follow_redirects=True)
 client.post("/profile",data={"name":"Updated Name","age":"23","blood_group":"A+"},follow_redirects=True)
 r=client.get("/dashboard");assert b"Updated Name" in r.data and b"Doctor questions" in r.data and b"Book appointment" in r.data
def test_sos_preview_not_sent_and_location_validation(client):
 register(client);login(client)
 r=client.post("/message/preview",data={"kind":"sos","latitude":"22.5726","longitude":"88.3639"})
 assert r.status_code==200 and b"NOT been sent" in r.data and b"112" in r.data and b"maps.google.com" in r.data
 r=client.post("/message/preview",data={"kind":"sos","latitude":"999","longitude":"999"})
 assert r.status_code==200 and b"invalid" in r.data.lower() and b"maps.google.com" not in r.data
def test_logout(client):
 register(client);login(client);client.post("/logout");assert client.get("/dashboard").status_code==302
