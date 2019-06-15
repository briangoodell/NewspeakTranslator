import json
import requests
import copy
from bs4 import BeautifulSoup
#import urllib.request as Request

def numSyns(word):
    tot = 0;
    url = "https://www.thesaurus.com/browse/" + word #Gets the thesaurus.com page corresponding to the given word
    word_responce = requests.get(url)
    bs = BeautifulSoup(word_responce.text,'html.parser')

    try:
        synsStrong = bs.findAll('a',{'class':'css-1dlcb58 etbu2a31'})
    except:
        synsStrong = []
    for i in synsStrong:
        tot += 1; #Maybe make this a scalar

    try:
        synsMed = bs.findAll('a',{'class':'css-y2bqzj etbu2a31'})
    except:
        synsMed = []
    for i in synsMed:
        tot += 1;

    try:
        synsWeak = bs.findAll('a',{'class':'css-y2bqzj etbu2a31'})
    except:
        synsWeak = []
    for i in synsWeak:
        tot += 1;

    return tot;

def synsTester(x):
    if x.lower() in short_words:
            new_text = new_text.replace(x + " ","",1)
            
    replacement = x
    url = "https://www.thesaurus.com/browse/" + x #Gets the thesaurus.com page corresponding to the given word
    word_responce = requests.get(url)
    bs = BeautifulSoup(word_responce.text,'html.parser')

    try:
        synsStrong = bs.findAll('a',{'class':'css-1dlcb58 etbu2a31'})
    except:
        synsStrong = []
    for i in synsStrong:
        if(len(i.get_text()) < len(replacement) and numSyns(i.get_text()) > numSyns(replacement)): 
            replacement = i.get_text()
    return(replacement)

def checkVerb(word):
    replacement = "N/A"
    form = "N/A"
    url = "https://www.merriam-webster.com/dictionary/" + word
    word_responce = requests.get(url)
    base_word = ""

    bs = BeautifulSoup(word_responce.text,'html.parser')
    potential_base=bs.findAll('a',{'class':'cxt text-uppercase'})
    if(potential_base != []):
        base_word = potential_base[0].get_text()

    potential_form = bs.findAll('span',{'class':'cxl'})
    if(potential_form != []):
        form = potential_form[0].get_text()

    if "entry" in base_word: #Occasionally dict.com returns that it's a plural
                             #of a certain type definition of a word (ex: lives)
        temp = base_word.split(' ')
        base_word = temp[0]
    
    if "past tense" in form:
        replacement = base_word + "ed"
    elif "plural of" in form:
        replacement = base_word + "s"

    if(replacement == word):
        replacement = "N/A"

    return(replacement)


def checkAdj(word, sentence = None): # "sentence = None"  allows me to call the funtion on words or as part of a larger sentence
    keep = True #This keeps track of whether or not we should be able to switch the replacement out with the origional word at the end
    adj_stay = ["good"]
    if word in adj_stay:
        return word
    if(word[len(word)-1] == ',' or word[len(word)-1] == '.'):
        word = word[0:len(word)-1] 
    replacement = "N/A"
    form = "N/A"
    url = "https://www.thesaurus.com/browse/" + word #Gets the thesaurus.com page corresponding to the given word
    word_responce = requests.get(url)
    bs = BeautifulSoup(word_responce.text,'html.parser')
    potential_type=bs.findAll('em',{'class':'css-u7frk4 e9i53te8'}) #Finds the part of speech given on the thesaurus.com page
    if(potential_type != []):
        form = potential_type[0].get_text()
    base_word = ""
    try:
        wide = bs.findAll('strong') #Finds the brief definition given on the thesaurus.com page
        base_word = wide[0].get_text()

##        splice = sentence.split(' ')
##        loc = splice.index(word)
##        try:
##            splice[loc + 1]
##        except:
##            form = "noun"
    except:
        print("NO THESAURUS DEFINITON FOR: " + word)

    base_word = base_word.replace("ly","")
    if(form == "adv."): #If adverb add the correct ending
        replacement = base_word + "wise"
    elif(form == "adj."): #If adjective add the correct ending
        replacement = base_word + "ful"
    elif(form == "noun"): #If noun revert back to original
        replacement = word
    
    if ' ' in base_word: #If definition has multiple words...
        print("MULTIWORD DEF for " + word)
        replacement = "N/A" 
        options = base_word.split(' ')
        for x in options: #...finds which word is the adjective, but is overwritten if a noun is present in the definition
            url2 = "https://www.merriam-webster.com/dictionary/" + x
            word_responce = requests.get(url2)
            bs2 = BeautifulSoup(word_responce.text,'html.parser')
            potential_type=bs2.findAll('a',{'class':'important-blue-link'})
            try:
                if(potential_type[0].get_text() == "adjective"):
                    if(form == "adv."):
                        replacement = x + "wise"
                    elif(form == "adj."):
                        replacement = x + "ful"
            except:
                replacement = word
        for x in options: #...finds which word is the noun and likely the newspeak noun-verb
            url2 = "https://www.merriam-webster.com/dictionary/" + x
            word_responce = requests.get(url2)
            bs2 = BeautifulSoup(word_responce.text,'html.parser')
            potential_type=bs2.findAll('a',{'class':'important-blue-link'})
            try:
                if(potential_type[0].get_text() == "noun"):
                    if(form == "adv."):
                        replacement = x + "wise"
                    elif(form == "adj."):
                        replacement = x + "ful"
    ##                elif(form == "noun"): 
    ##                    replacement = x
            except:
                replacement = word
        
    else:
        x = replacement
       
    #Checks if antonym
    try:
        antonyms_wide = bs.findAll('a',{'class':'css-14o1rmz etbu2a31'})
    except:
        antonyms_wide = []
    antonyms = []
    for i in antonyms_wide:
        antonyms.append(i.get_text())
    if x in antonyms:
        replacement = "un" + replacement
        keep = False #If its the opposite it should be able to revert (dark -> unlight)

    replacement = replacement.replace(",","") #This gets rid of any commas
    replacement = replacement.replace(".","") #This gets rid of any periods

    if(len(word) < len(base_word) and keep):
        replacement = word

    if(replacement == word):
        replacement = "N/A"
        
    return(replacement)

#########################################Spell Checking With Microsoft's API#########################################

##url = "https://api.cognitive.microsoft.com/bing/v7.0/spellcheck"
##api_key = "YOUR KEY"
input_text = input('Old Speak-> ')
if(input_text == "%FILE"):
    print("FILE TRANSLATON MODE")
    file_name = input('File Name: ')
    file = open(file_name,'r')
    input_text = file.read()
    #print(input_text)
##
##data = {'text': input_text}
##params = {
##    'mkt':'en-us',
##    'mode':'proof'
##    }
##headers = {
##    'Content-Type': 'application/x-www-form-urlencoded',
##    'Ocp-Apim-Subscription-Key': api_key,
##    }
##
##responce = requests.post(url, headers=headers, params=params, data=data)
##test = responce.json()
##
##suggested = test.get('flaggedTokens')
##
new_text = copy.deepcopy(input_text)
##for x in suggested:
##    suggestion = x.get('suggestions')
##    word = suggestion[0].get('suggestion')
##    old_word = x.get('token')
##    new_text = new_text[0:x.get('offset')] + word + new_text[(len(old_word)+x.get('offset')): len(new_text)]
##    
##    
###loc = test.get('iss_position')
###text = loc.get('latitude')
##if(input_text != new_text):
##    print("Auto-corrected: " + new_text)


#########################################Spell Checking using a Google search#########################################
chkd = "N/A"
txt = new_text.replace(' ','+')
url = "https://www.google.com/search?q=" + txt #Does a google search of the term
google_resp = requests.get(url)
google = BeautifulSoup(google_resp.text,'html.parser')
potential_chks=google.findAll('a',{'id':'scl'})


try:
    chkd = potential_chks[0].get_text()
except:
    chkd = new_text
new_text = chkd
print("AUTO-CORRECTED TO: " + new_text)

#########################################Actual Main Part#########################################

#,"":""
while(new_text[len(new_text)-1] == ' '): #Gets rid of potential whitespace at the end of the user input
    new_text = new_text[0:len(new_text) - 1]
while(new_text[0] == ' '): #Gets rid of potential whitespace at the start of the user input
    new_text = new_text[1:len(new_text)]
noun_dict = {"england":"Airstrip One","England":"Airstrip One","leader":"Big Brother","Queen":"Big Brother","queen":"Big Brother","president":"Big Brother","English Socalism":"Ingsoc",
                    "televison":"telescreen","TV":"telescreen","organization":"comintern"}
verb_dict = {"shall":"should","will":"would","cut":"knife","slow":"unspeedful","fast":"speedful","bad":"ungood"}
replace_doubleplus = ["absolutely","exceedingly","incredibly","greatly","profoundly","extraordinarily","extremely"]
replace_plus = ["very","remarkably","considerably","amply"]
short_words = ["this","and","a","the","in","that","to","of","these","be","from"] #Words to be removed
idioms = {"different light":"different way","A blessing in disguise":"a good thing that seemed bad at first","A dime a dozen":"Something common","Beat around the bush":"Avoid saying what you mean, usually because it is uncomfortable","Better late than never":"Better to arrive late than not to come at all","Bite the bullet":"To get something over with because it is inevitable","Break a leg":"Good luck","Call it a day":"Stop working on something","Cut somebody some slack":"Don't be so critical","Cutting corners":"Doing something poorly in order to save time or money","Easy does it":"Slow down","Get out of hand":"Get out of control","Get something out of your system":"Do the thing you've been wanting to do so you can move on","Get your act together":"Work better or leave","Give someone the benefit of the doubt":"Trust what someone says","Go back to the drawing board":"Start over","Hang in there":"Don't give up","Hit the sack":"Go to sleep","It's not rocket science":"It's not complicated","Let someone off the hook":"To not hold someone responsible for something","Make a long story short":"Tell something briefly","Miss the boat":"It's too late","No pain, no gain":"You have to work for what you want","On the ball":"Doing a good job","Pull someone's leg":"To joke with someone","Pull yourself together":"Calm down","So far so good":"Things are going well so far","Speak of the devil":"The person we were just talking about showed up!","That's the last straw":"My patience has run out","The best of both worlds":"An ideal situation","Time flies when you're having fun":"You don't notice how long something lasts when it's fun","To get bent out of shape":"To get upset","To make matters worse":"Make a problem worse","Under the weather":"Sick","We'll cross that bridge when we come to it":"Let's not talk about that problem right now","Wrap your head around something":"Understand something complicated","You can say that again":"That's true, I agree","Your guess is as good as mine":"I have no idea"}

decl_of_ind = open("decInd.txt","r") #Opens the text of the declaration of independence

if new_text in decl_of_ind.read() and len(new_text.split(' ')) > 2: #Checks for any continuity with the declaration of independence
    print("CRIMETHINK")

for x in idioms:
    new_text = new_text.replace(x,idioms[x])

new_text = new_text.replace("could not","uncould") #These are just exceptions that needed to be hard coded
new_text = new_text.replace(" of ","")
for v in short_words:
    cap_word = v[0].upper() + v[1:len(v)] + ' '
    new_text = new_text.replace(cap_word,"")
    new_text = new_text.replace(" " + v + " "," ")

done = False
words = new_text.split(' ')
for i in words:
    i = i.replace(',','')
    i = i.replace('.','')
    i = i.replace('!','')
    i = i.replace('?','')
    done = True #Changes it here so itll only change back if none of the ifs are triggered (its not a special case)
            
    if i in noun_dict:
        new_text = new_text.replace(i,noun_dict[i],1)
        if (words[words.index(i)-1] == "the" or words[words.index(i)-1] == "a"):
            wrdandspace = words[words.index(i)-1] + " " + noun_dict[i]
            new_text = new_text.replace(wrdandspace,noun_dict[i],1)
        
##        print(new_text)
    elif i in replace_doubleplus:
        new_text = new_text.replace(i,"doubleplus")
    elif i in replace_plus:
        new_text = new_text.replace(i,"plus")
    else:
        done = False
        
    url = "https://www.merriam-webster.com/dictionary/" + i
    word_responce = requests.get(url)
    bs = BeautifulSoup(word_responce.text,'html.parser')
    part_of_speech=bs.findAll('a',{'class':'important-blue-link'})

    try:
        first_def=bs.findAll('span',{'class':'dtText'})
        if "color" in first_def[0].get_text():
            done = True
    except:
        done = True
    try: #This is because some words, like swam, dont have PoS in their definitions, but nouns always have "noun" so we can determine they're not nouns and the if is still fufilled
        if(part_of_speech[0].get_text() != "noun" and not done):
            new_verb = checkVerb(i)
            if(new_verb != "N/A"):
                new_text = new_text.replace(i,new_verb,1)
                print("VERB CHANGED: " + new_text)
            elif(len(i) > 3 and i != "that"): #Detects "in" as "fashionable" and "that" as "the"
                new_adj = checkAdj(i, sentence = new_text)
                if(new_adj != "N/A"):
                    new_text = new_text.replace(i,new_adj,1)
                    print("Changed " + i + " to " + new_adj + ": " + new_text)
        elif(part_of_speech[0].get_text() == "noun" and not done):
            syn = synsTester(i)
            new_text = new_text.replace(i,syn,1)
            
    except:
        new_verb = checkVerb(i)
        if(new_verb != "N/A"):
            new_text = new_text.replace(i,new_verb,1)
            print("VERB CHANGED: " + new_text)
        if(len(i) > 3 and i != "that"): #Detects "in" as "fashionable" and "that" as "the"
            new_adj = checkAdj(i, sentence = new_text)
            if(new_adj != "N/A"):
                new_text = new_text.replace(i,new_adj,1)
                print("Changed " + i + " to " + new_adj + ": " + new_text)
    
print("")
print("NEWSPEAK: " + new_text)
