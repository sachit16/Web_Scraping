from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
from flask import send_file
from bson import ObjectId
import pymongo 

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            
            flipkartPage = uClient.read()
            uClient.close()

            #flipkartPage = uClient.read()
            #uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            filename = searchString + ".csv"
            #csvfile=open(filename, "w", newline='', encoding='utf-8')  
            #fw = open(filename, "w")
            #csvwriter = csv.writer(csvfile)
            headers = ["Product", "Name", "Rating", "CommentHead", "Comment"]
            #csvwriter.writerow(headers)
            del bigboxes[0:3]
            del bigboxes[22:]
            reviews = []
            for box in bigboxes:
                #box = bigboxes[3]
                productLink ="https://www.flipkart.com"+box.div.div.div.a["href"]
                prodRes = requests.get(productLink)
                prodRes.encoding='utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                #print(prod_html)
                commentboxes =prod_html.findAll("div",{"class":"_16PBlm"})

               
                
                for commentbox in commentboxes:
                    try:
                        #name.encode(encoding='utf-8')
                        name = commentbox.div.div.find_all('p',{'class':'_2sc7ZR _2V5EHH'})[0].text
                        #print(name)

                    except:
                        logging.info("name")
                    try:
                        #rating.encode(encoding='utf-8')
                        rating = commentbox.div.div.div.div.text
                        #print(rating)


                    except:
                        rating = 'No Rating'
                        logging.info("rating")
                    try:
                        #commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.div.div.div.p.text
                        #print(commentHead)
                    
                    except:
                        commentHead = 'No Comment Heading'
                        logging.info(commentHead)
                    try:
                        comtag = commentbox.div.div.find_all("div",{"class":""})[0].div.text
                        #custComment.encode(encoding='utf-8')
                        #custComment = comtag[0].div.text
                    except Exception as e:
                        logging.info(e)

               
                    mydict = {"_id": str(ObjectId()),"Product": searchString, "Name": name,"Rating":rating,"CommentHead":commentHead,"Comment": str(comtag) if isinstance(comtag, ObjectId) else comtag}
                    print(mydict)
                    reviews.append(mydict)
                    #csvwriter.writerow([mydict["Product"], mydict["Name"], mydict["Rating"], mydict["CommentHead"], mydict["Comment"]])
                    #logging.info("log my final result {}".format(reviews))
            #client = pymongo.MongoClient("mongodb+srv://sachit:Pass@cluster0.im7zjfw.mongodb.net/?retryWrites=true&w=majority")
            #db = client['scrapping_data_base']
            #review_col = db['review_Scraping_Data']
            #review_col.insert_many(reviews)
            #for review in reviews:
              #  review_col.insert_one(review)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            #logging.exception("An exception occurred: {}".format(str(e)))
            return 'An exception occurred: {}'.format(str(e))

    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)
