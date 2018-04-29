import psycopg2
from flask import render_template
from app import app
import datetime
import tld



conn = psycopg2.connect("host=192.168.3.15 dbname=eight user=mikem_read password=54321")
cur = conn.cursor()




# bandcamp generation
dt = datetime.datetime.now() - datetime.timedelta(7)
cur.execute("SELECT * FROM bandcamp WHERE published > (%s)", (dt,))
bc_rows = cur.fetchall()
conn.commit()

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


# youtube generation
cur.execute("SELECT * FROM youtube;  ")
yt_rows = cur.fetchall()
conn.commit()

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



# images generation
dt = datetime.datetime.now() - datetime.timedelta(2)
cur.execute("SELECT * FROM images WHERE date > (%s)", (dt,))
img_rows = cur.fetchall()
conn.commit()

img_rows = sorted(img_rows, key=lambda x: x[1], reverse=True)

img_posts =[]
for x in img_rows:
    di = {'img' : x[3].split('/',1)[-1] }
    img_posts.append(di)


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html', zero=bc_zero, cost=bc_cost, yt=yt_posts, imgs = img_posts)


