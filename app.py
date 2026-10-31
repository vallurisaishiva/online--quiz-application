import time
from flask import Flask,render_template,request,redirect,url_for,session
from config import Config
from db import get_connection
app=Flask(__name__); app.config.from_object(Config); DURATION=300

def questions():
    c=get_connection()
    try:
        cur=c.cursor(dictionary=True); cur.execute("SELECT id,question_text,category FROM questions ORDER BY id"); rows=cur.fetchall()
        for q in rows:
            cur.execute("SELECT id,option_text FROM options WHERE question_id=%s ORDER BY id",(q["id"],)); q["options"]=cur.fetchall()
        return rows
    finally: c.close()

@app.route("/")
def index():
    c=get_connection()
    try:
        cur=c.cursor(); cur.execute("SELECT COUNT(*) FROM questions"); n=cur.fetchone()[0]
    finally: c.close()
    return render_template("index.html",question_count=n,duration=DURATION//60)

@app.post("/start")
def start():
    qs=questions()
    if not qs: return redirect(url_for("index"))
    session["ids"]=[q["id"] for q in qs]; session["started"]=time.time()
    return redirect(url_for("quiz"))

@app.route("/quiz")
def quiz():
    ids=session.get("ids")
    if not ids: return redirect(url_for("index"))
    qs=[q for q in questions() if q["id"] in ids]
    return render_template("quiz.html",questions=qs,duration=DURATION)

@app.post("/submit")
def submit():
    ids=session.get("ids")
    if not ids: return redirect(url_for("index"))
    expired=time.time()-session.get("started",time.time())>DURATION+10
    c=get_connection(); score=0; review=[]
    try:
        cur=c.cursor(dictionary=True)
        for qid in ids:
            cur.execute("SELECT question_text FROM questions WHERE id=%s",(qid,)); q=cur.fetchone()
            cur.execute("SELECT id,option_text,is_correct FROM options WHERE question_id=%s",(qid,)); opts=cur.fetchall()
            selected_id=None if expired else request.form.get("question_"+str(qid),type=int)
            selected=next((o for o in opts if o["id"]==selected_id),None)
            correct=next((o for o in opts if o["is_correct"]),None)
            good=bool(selected and selected["is_correct"]); score+=int(good)
            review.append({"question":q["question_text"],"selected":selected["option_text"] if selected else "Not answered","correct":correct["option_text"] if correct else "Not configured","is_correct":good})
    finally: c.close()
    total=len(ids); session.pop("ids",None); session.pop("started",None)
    return render_template("result.html",score=score,total=total,percentage=round(score/total*100) if total else 0,review=review,expired=expired)

if __name__=="__main__": app.run(port=5001,debug=True)
