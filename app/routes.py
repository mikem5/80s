import psycopg2
from flask import render_template
from app import app
import datetime
import tld



# read db info from local file
with open('/var/www/80s/app/db.info', 'r') as dbfile:
    db_pw = dbfile.read().rstrip()



# pull from database depending on which table
def db_pull(table):


    # establish db connection
    conn = psycopg2.connect(db_pw)

    # need this or remote server breaks
    conn.set_client_encoding("utf-8")
    cur = conn.cursor()

    if table == 'bandcamp':
        dt = datetime.datetime.now() - datetime.timedelta(7)
        cur.execute("SELECT * FROM bandcamp WHERE published > (%s)", (dt,))
    
    if table == 'youtube':
        cur.execute("SELECT * FROM youtube;  ")

    if table == 'images':
        dt = datetime.datetime.now() - datetime.timedelta(2)
        cur.execute("SELECT * FROM images WHERE date > (%s)", (dt,))


    rows = cur.fetchall()
    conn.commit()
    conn.close()

    return rows




# bandcamp generation
def bandcamp_sort():

    bc_rows = db_pull('bandcamp')

    bc_rows = sorted(bc_rows, key=lambda x: x[6], reverse=True)

    bc_cost = []
    bc_zero = []

    for x in bc_rows:
        if x[6] < datetime.datetime.now():

            di = {'meta': " - ".join([x[3],x[4]]),
                'img' :x[7].split('/',1)[1],
                'price': x[5],
                'date' : x[6],
                'url' : x[2]
                }
            if x[5] == '0':
                bc_zero.append(di)
            else:
                bc_cost.append(di)
        else:
            pass

    # returns a tuple
    return (bc_zero, bc_cost)





# youtube generation
def youtube_sort():
    
    yt_rows = db_pull('youtube')

    yt_rows = sorted(yt_rows, key=lambda x: x[1], reverse=True)

    yt_posts = []

    for i in range(8):
        x = yt_rows[i]
        if tld.get_tld(x[2]) == 'youtu.be':

            di = {'id': x[2].split('/')[-1]
                }
        else:
            di = {'id': x[2].split('=')[-1]
                }
        yt_posts.append(di)

    return yt_posts




# images generation
def image_sort():

    img_rows = db_pull('images')

    img_rows = sorted(img_rows, key=lambda x: x[1], reverse=True)

    img_posts =[]
    for x in img_rows:
        di = {'img' : x[3].split('/',1)[-1] }
        img_posts.append(di)


    return img_posts




@app.route('/')
@app.route('/index')
def index():

    (bc_z, bc_c) = bandcamp_sort()
    yt_p = youtube_sort()
    img_p = image_sort()


    return render_template('index.html', zero=bc_z, cost=bc_c, yt=yt_p, imgs = img_p)


