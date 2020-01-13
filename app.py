import flask
import pickle
import tweepy #https://github.com/tweepy/tweepy
import csv
import datetime
import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics


#with open(f'model/twbot_200.pkl', 'rb') as f:
#    model = pickle.load(f)

app = flask.Flask(__name__, template_folder='templates')   

    
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('main.html'))
    
    if flask.request.method == 'POST':
        t_user = flask.request.form['twitter-user']
        
        #Twitter API credentials
        credentials={}
        credentials['consumer_key']='jQWSWqQNHhIAsaD878NAHZTOB'
        credentials['consumer_secret']= 'ycfTPsE6rGtce9IA1yCh51UQyH87bRcVzvhdM72mbw6sVjxrjA'
        credentials['access_token']='231187129-5tDWxdufIs1gtYCI3nnlmFcaTUnQq69f5ywlGagR'
        credentials['access_token_secret']= 'mDwALrKEOeQDiLQYjcXVAz55mZImflpv3fLWj4YVgivNK'

        # Save the credentials object to file
        with open("twitter_credentials.json", "w") as file:
            json.dump(credentials, file)

            #Twitter only allows access to a users most recent 3240 tweets with this method

            #authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
        api = tweepy.API(auth, wait_on_rate_limit=True)


        user_id = []
        screen_name = []
        tweets = []
        followers = []
        favs = []
        friends = []
        bios = []
        phone = []
        creation_date = []
        verified = []
        
        twitter_user = [None] * 1
        twitter_user[0] = t_user

        for u in twitter_user:
            user = api.get_user(u)
            user_id.append(user.id)
            screen_name.append(user.screen_name)
            tweets.append(user.statuses_count)
            followers.append(user.followers_count)
            favs.append(user.favourites_count)
            friends.append(user.friends_count)
            bios.append(user.description)
            creation_date.append(user.created_at)


        zipped_data = zip(user_id, screen_name, tweets, followers, favs, friends, bios, creation_date)

        # Creates a pandas dataframe containing user attributes
        input_df = pd.DataFrame(list(zipped_data), columns=['user_id', 
                                                             'screen_name',
                                                             'tweets',
                                                             'followers',
                                                             'favs',
                                                             'friends',
                                                             'bios',
                                                             'creation_date'])

        input_df['creation_date'] = input_df['creation_date'].dt.date
        current_date = datetime.date.today()
        input_df['account_age']  = current_date - input_df['creation_date']
        input_df['account_age'] = input_df['account_age'].dt.days.astype('int16')
        input_df['favs_frequency'] = input_df['favs'] / input_df['account_age']
        input_df['tweet_frequency'] = input_df['tweets'] / input_df['account_age']

        dataset_df = pd.read_csv('file3.csv')

        X = dataset_df[['tweets', 'followers', 'favs', 'friends', 'account_age', 'favs_frequency', 'tweet_frequency']].values
        y = dataset_df['bot']


        X_trainset, X_testset, y_trainset, y_testset = train_test_split(X, y, test_size=0.3, random_state=3)


        ## modeling

        botTree = DecisionTreeClassifier(criterion="gini", max_depth = 6)
        
        botTree.fit(X_trainset,y_trainset)

        Xnew = input_df.loc[0,['tweets', 'followers', 'favs', 'friends', 'account_age', 'favs_frequency', 'tweet_frequency']].values

        Xnew = Xnew.reshape(1, -1)
        
        predTree = botTree.predict(Xnew)
        

        if predTree == 0:
            result = "@%s is not a bot" % (t_user)
        
        elif predTree == 1:
            result = "@%s is likely to be a bot" % (t_user)


        #input_variables = twitter_user
        #prediction = model.predict(input_variables)
        
        return flask.render_template('main.html',original_input={'twitter-user':t_user}, result=result, scraping=Xnew)
                                                                 
        if __name__ == '__main__':
            app.run()
