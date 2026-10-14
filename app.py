import os,secrets
from pathlib import Path
from datetime import date,datetime,timedelta
from functools import wraps
from flask import Flask,abort,flash,redirect,render_template,request,session,url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash,generate_password_hash

db=SQLAlchemy(); csrf=CSRFProtect(); limiter=Limiter(key_func=get_remote_address,default_limits=["200 per day","50 per hour"])
MOODS=["Happy","Neutral","Sad","Irritable","Anxious","Tired","Energetic"]
REMINDERS=["Period","Medication","Health checkup","Vitamins","Exercise","Other"]
TIPS=[("Stay aware","Pay attention to your surroundings and trust your instincts."),("Share your plan","Tell someone trusted where you are going and when you expect to return."),("Choose safer routes","Prefer well-lit, populated routes and trusted transport."),("Keep a charged phone","Save trusted contacts and emergency numbers."),("Move toward people","Go toward a staffed or populated place if you feel unsafe."),("Ask for help","In India, call 112 for emergency assistance when safe.")]
HEALTH_TIPS=["Drink water regularly; hydration may help with bloating and cramps.","Include iron-rich foods such as lentils and leafy greens.","Gentle movement or stretching may help some period symptoms.","Try to keep a consistent sleep schedule.","Track your cycle for several months to understand your own patterns.","For severe or disruptive symptoms, consult a qualified clinician.","Your mood matters too; note stress and sleep alongside symptoms.","Cycle estimates are not diagnosis or contraception advice."]
class User(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(80),nullable=False); age=db.Column(db.Integer)
 email=db.Column(db.String(254),unique=True,nullable=False,index=True); password_hash=db.Column(db.String(255),nullable=False); blood_group=db.Column(db.String(8),default="")
class Contact(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True); name=db.Column(db.String(80),nullable=False); phone=db.Column(db.String(32),nullable=False); relation=db.Column(db.String(40),default="")
class Cycle(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True); start_date=db.Column(db.Date,nullable=False); end_date=db.Column(db.Date); cycle_length=db.Column(db.Integer,default=28,nullable=False); notes=db.Column(db.String(500),default="")
class Symptom(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True); log_date=db.Column(db.Date,default=date.today,nullable=False)
 headache=db.Column(db.Boolean,default=False); cramps=db.Column(db.Boolean,default=False); fatigue=db.Column(db.Boolean,default=False); bloating=db.Column(db.Boolean,default=False); mood=db.Column(db.String(24),default=""); notes=db.Column(db.String(500),default="")
class Note(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True); title=db.Column(db.String(120),nullable=False); content=db.Column(db.String(3000),default=""); created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
class Reminder(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True); reminder_type=db.Column(db.String(40),nullable=False); message=db.Column(db.String(240),nullable=False); remind_date=db.Column(db.Date,nullable=False); is_done=db.Column(db.Boolean,default=False,nullable=False)

def create_app(test_config=None):
 app=Flask(__name__,instance_relative_config=True); secret=os.environ.get("SECRET_KEY")
 if not secret and (os.environ.get("RENDER") or os.environ.get("FLASK_DEBUG")=="0"): raise RuntimeError("Set SECRET_KEY in the production environment.")
 app.config.update(SECRET_KEY=secret or secrets.token_hex(32),SQLALCHEMY_TRACK_MODIFICATIONS=False,MAX_CONTENT_LENGTH=1024*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER") or os.environ.get("COOKIE_SECURE")=="1"),PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
 if test_config: app.config.update(test_config)
 Path(app.instance_path).mkdir(parents=True,exist_ok=True); uri=os.environ.get("DATABASE_URL")
 if uri:
  if uri.startswith("postgres://"): uri="postgresql+psycopg://"+uri[len("postgres://"):]
  elif uri.startswith("postgresql://"): uri="postgresql+psycopg://"+uri[len("postgresql://"):]
  app.config["SQLALCHEMY_DATABASE_URI"]=uri
 else:
  path=Path(os.environ.get("DATABASE_PATH",str(Path(app.instance_path)/"girls_safety.db"))).resolve(); app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+str(path); app.config["SQLALCHEMY_ENGINE_OPTIONS"]={"connect_args":{"check_same_thread":False}}
 db.init_app(app); csrf.init_app(app); limiter.init_app(app)
 @app.after_request
 def security_headers(r):
  for k,v in {"X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"strict-origin-when-cross-origin","Permissions-Policy":"geolocation=(self)","Cache-Control":"no-store"}.items(): r.headers.setdefault(k,v)
  if request.is_secure or os.environ.get("RENDER"): r.headers.setdefault("Strict-Transport-Security","max-age=31536000; includeSubDomains")
  return r
 with app.app_context(): db.create_all()
 def current_user():
  return db.session.get(User,session.get("user_id")) if session.get("user_id") else None
 app.jinja_env.globals["current_user"]=current_user
 def required(fn):
  @wraps(fn)
  def inner(*a,**kw):
   if not current_user(): flash("Please log in to view your private dashboard.","info"); return redirect(url_for("login"))
   return fn(*a,**kw)
  return inner
 def day(value,label):
  try:return date.fromisoformat(value or "")
  except (ValueError,TypeError):raise ValueError("Enter a valid "+label+".")
 def owned(model,rid):
  obj=db.session.get(model,rid)
  if not obj or obj.user_id!=current_user().id:abort(404)
  return obj
 @app.get("/healthz")
 def healthz():
  try:db.session.execute(db.text("SELECT 1"));return {"status":"ok"},200
  except Exception:app.logger.exception("DB health check failed");return {"status":"unavailable"},503
 @app.get("/")
 def home():return redirect(url_for("dashboard")) if current_user() else render_template("page.html",view="landing")
 @app.route("/register",methods=["GET","POST"])
 @limiter.limit("5 per minute",methods=["POST"])
 def register():
  if request.method=="POST":
   name=request.form.get("name","").strip();email=request.form.get("email","").strip().lower();pw=request.form.get("password","");raw=request.form.get("age","").strip();blood=request.form.get("blood_group","")
   try:
    age=int(raw) if raw else None
    if not name or len(name)>80:raise ValueError("Enter a name up to 80 characters.")
    if not email or len(email)>254 or "@" not in email:raise ValueError("Enter a valid email address.")
    if len(pw)<10:raise ValueError("Use a password with at least 10 characters.")
    if age is not None and not 1<=age<=120:raise ValueError("Age must be between 1 and 120.")
    if blood and blood not in {"A+","A-","B+","B-","AB+","AB-","O+","O-"}:raise ValueError("Choose a valid blood group.")
   except ValueError as e:flash(str(e),"error");return render_template("page.html",view="register"),400
   db.session.add(User(name=name,email=email,age=age,blood_group=blood,password_hash=generate_password_hash(pw,method="scrypt")))
   try:db.session.commit()
   except IntegrityError:db.session.rollback();flash("Email already registered. Please log in.","error");return render_template("page.html",view="register"),409
   flash("Account created. Please log in.","success");return redirect(url_for("login"))
  return render_template("page.html",view="register")
 @app.route("/login",methods=["GET","POST"])
 @limiter.limit("10 per minute",methods=["POST"])
 def login():
  if request.method=="POST":
   u=User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
   if not u or not check_password_hash(u.password_hash,request.form.get("password","")):flash("Email or password is incorrect.","error");return render_template("page.html",view="login"),401
   session.clear();session["user_id"]=u.id;session.permanent=True;flash("Welcome back, "+u.name+"!","success");return redirect(url_for("dashboard"))
  return render_template("page.html",view="login")
 @app.post("/logout")
 def logout():session.clear();flash("You have been logged out.","info");return redirect(url_for("home"))
 @app.get("/dashboard")
 @required
 def dashboard():
  u=current_user();cycles=Cycle.query.filter_by(user_id=u.id).order_by(Cycle.start_date.desc()).limit(6).all();symptoms=Symptom.query.filter_by(user_id=u.id).order_by(Symptom.log_date.desc()).limit(5).all()
  contacts=Contact.query.filter_by(user_id=u.id).order_by(Contact.name).all();notes=Note.query.filter_by(user_id=u.id).order_by(Note.created_at.desc()).limit(10).all();reminders=Reminder.query.filter_by(user_id=u.id,is_done=False).order_by(Reminder.remind_date).all()
  phase=None;next_period=None
  if cycles:
   avg=round(sum(c.cycle_length for c in cycles[:3])/len(cycles[:3]));next_period=cycles[0].start_date+timedelta(days=avg);d=(date.today()-cycles[0].start_date).days%avg+1
   phase={"name":"Menstrual" if d<=5 else "Follicular" if d<=13 else "Ovulation" if d<=16 else "Luteal","day":d,"length":avg}
  summary={k:sum(bool(getattr(s,k)) for s in symptoms) for k in ("headache","cramps","fatigue","bloating")} if symptoms else None
  return render_template("page.html",view="dashboard",user=u,cycles=cycles,symptoms=symptoms,contacts=contacts,notes=notes,reminders=reminders,phase=phase,next_period=next_period,summary=summary,today=date.today().isoformat(),tip=HEALTH_TIPS[date.today().timetuple().tm_yday%len(HEALTH_TIPS)],moods=MOODS,reminder_types=REMINDERS,safety_tips=TIPS)
 @app.post("/profile")
 @required
 def profile():
  u=current_user();name=request.form.get("name","").strip();raw=request.form.get("age","").strip();blood=request.form.get("blood_group","")
  try:
   age=int(raw) if raw else None
   if not name or len(name)>80 or (age is not None and not 1<=age<=120):raise ValueError("Enter a valid name and age.")
   if blood and blood not in {"A+","A-","B+","B-","AB+","AB-","O+","O-"}:raise ValueError("Choose a valid blood group.")
  except ValueError as e:flash(str(e),"error");return redirect(url_for("dashboard")+"#profile")
  u.name,u.age,u.blood_group=name,age,blood;db.session.commit();flash("Profile updated.","success");return redirect(url_for("dashboard")+"#profile")
 @app.post("/contacts")
 @required
 def add_contact():
  n=request.form.get("name","").strip();p=request.form.get("phone","").strip();rel=request.form.get("relation","").strip()
  if not n or len(n)>80 or not p or len(p)>32 or len(rel)>40:flash("Enter a valid contact name and phone.","error")
  else:db.session.add(Contact(user_id=current_user().id,name=n,phone=p,relation=rel));db.session.commit();flash("Contact saved; no automatic call or message is made.","success")
  return redirect(url_for("dashboard")+"#safety")
 @app.post("/contacts/<int:rid>/delete")
 @required
 def delete_contact(rid):
  o=owned(Contact,rid);db.session.delete(o);db.session.commit();flash("Contact deleted.","success");return redirect(url_for("dashboard")+"#safety")
 @app.post("/cycles")
 @required
 def add_cycle():
  try:
   start=day(request.form.get("start_date"),"period start date");raw=request.form.get("end_date","").strip();end=day(raw,"period end date") if raw else None;length=int(request.form.get("cycle_length","28"));notes=request.form.get("notes","").strip()
   if start>date.today():raise ValueError("Start date cannot be in the future.")
   if end and (end<start or end>start+timedelta(days=14)):raise ValueError("End date must be within 14 days after start.")
   if not 21<=length<=45 or len(notes)>500:raise ValueError("Cycle length must be 21–45 days and notes at most 500 characters.")
  except ValueError as e:flash(str(e),"error");return redirect(url_for("dashboard")+"#health")
  db.session.add(Cycle(user_id=current_user().id,start_date=start,end_date=end,cycle_length=length,notes=notes));db.session.commit();flash("Period log saved; predictions are estimates.","success");return redirect(url_for("dashboard")+"#health")
 @app.post("/symptoms")
 @required
 def add_symptom():
  try:
   d=day(request.form.get("log_date"),"symptom date");m=request.form.get("mood","");notes=request.form.get("notes","").strip()
   if d>date.today() or (m and m not in MOODS) or len(notes)>500:raise ValueError("Check the date, mood and notes.")
  except ValueError as e:flash(str(e),"error");return redirect(url_for("dashboard")+"#health")
  db.session.add(Symptom(user_id=current_user().id,log_date=d,mood=m,notes=notes,headache="headache" in request.form,cramps="cramps" in request.form,fatigue="fatigue" in request.form,bloating="bloating" in request.form));db.session.commit();flash("Symptom log saved.","success");return redirect(url_for("dashboard")+"#health")
 @app.post("/notes")
 @required
 def add_note():
  t=request.form.get("title","").strip();c=request.form.get("content","").strip()
  if not t or len(t)>120 or len(c)>3000:flash("Enter a title up to 120 characters; note limit is 3,000.","error")
  else:db.session.add(Note(user_id=current_user().id,title=t,content=c));db.session.commit();flash("Private health note saved.","success")
  return redirect(url_for("dashboard")+"#notes")
 @app.post("/notes/<int:rid>/delete")
 @required
 def delete_note(rid):
  o=owned(Note,rid);db.session.delete(o);db.session.commit();flash("Note deleted.","success");return redirect(url_for("dashboard")+"#notes")
 @app.post("/reminders")
 @required
 def add_reminder():
  kind=request.form.get("reminder_type","");msg=request.form.get("message","").strip()
  try:
   d=day(request.form.get("remind_date"),"reminder date")
   if kind not in REMINDERS or not msg or len(msg)>240:raise ValueError("Choose a type and enter a message up to 240 characters.")
  except ValueError as e:flash(str(e),"error");return redirect(url_for("dashboard")+"#reminders")
  db.session.add(Reminder(user_id=current_user().id,reminder_type=kind,message=msg,remind_date=d));db.session.commit();flash("Reminder saved.","success");return redirect(url_for("dashboard")+"#reminders")
 @app.post("/reminders/<int:rid>/done")
 @required
 def done_reminder(rid):
  o=owned(Reminder,rid);o.is_done=True;db.session.commit();flash("Reminder marked done.","success");return redirect(url_for("dashboard")+"#reminders")
 @app.post("/message/preview")
 @required
 def message_preview():
  kind=request.form.get("kind","sos")
  if kind not in {"sos","share"}:abort(400)
  lat=lon=None
  try:
   if request.form.get("latitude") and request.form.get("longitude"):
    lat=float(request.form["latitude"]);lon=float(request.form["longitude"])
    if not(-90<=lat<=90 and -180<=lon<=180):raise ValueError()
  except ValueError:lat=lon=None;flash("Invalid coordinates omitted.","warning")
  link=f"https://maps.google.com/?q={lat},{lon}" if lat is not None else None;place="Browser location supplied with permission" if link else "Location not provided or permission denied";stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S");name=current_user().name
  if kind=="sos":heading="SOS message preview";msg=f"EMERGENCY SOS — I need help. My name is {name}.\\nLocation: {place}\\n"+(f"Map: {link}\\n" if link else "No location coordinates available.\\n")+f"Prepared at: {stamp}\\nThis message has NOT been sent.\\nIndia emergency: 112 | Women helpline: 1091"
  else:heading="Location-sharing message preview";msg=f"Location update from {name}\\nLocation: {place}\\n"+(f"Map: {link}\\n" if link else "No location coordinates available.\\n")+f"Time: {stamp}\\nThis message has NOT been sent."
  return render_template("page.html",view="preview",heading=heading,message=msg,map_link=link)
 @app.errorhandler(413)
 def too_large(_e):return "Request too large.",413
 return app
app=create_app()
if __name__=="__main__":app.run(host="127.0.0.1",port=int(os.environ.get("PORT","5000")),debug=False)
