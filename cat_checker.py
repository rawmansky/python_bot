from clarifai.rest import ClarifaiApp, client, Image
import pprint

def img_has_cat(filename):#url):
    app = ClarifaiApp(api_key="ee15b61906ee4423b5c9bea34977228d")
    model = app.models.get("general-v1.3")
    
    try:
        image = Image(file_obj=open(filename, 'rb'))
        #result = model.predict_by_url(url=url)
        result = model.predict([image])
        try:
            items = result['outputs'][0]['data']['concepts']
            for item in items:
                if item['name'] == 'cat':
                    return True
            else:
                return False
        except (IndexError):
            return False
    except (client.ApiError):
        return False
        
if __name__ == "__main__":
    #print(img_has_cat("http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg"))
    #print(img_has_cat("http://images2.fanpop.com/image/photos/11700000/Catwomen-3-catwomen-11767352-600-900.jpg"))
    #print(img_has_cat("http://images2.fanpop.com/image/photos/11700000/Catwomen-3-catwomen-11"))
    print(img_has_cat("cats/cat1.jpg"))

    
    #pp = pprint.PrettyPrinter(indent=2)
    #print(result)
    #pp.pprint(result['outputs'][0]['data']['concepts'])