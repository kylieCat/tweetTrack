tweetTrack
==========

A python based project that explores locating twitter users through their tweeting style.

This project aims to replicate the research done by Mahmud, Nichols, & Drews (in press). http://arxiv.org/ftp/arxiv/papers/1403/1403.2345.pdf, and create a classifier to predict the geolocation of Twitter users based on analysis of the contents of their tweets. The original project created three classifiers: one being fed all the words in the tweets in a training set, one being fed only place names, and one being fed only time stamps. For our week-long project, we replicated the first of these three classifiers. 

Our user interface is a website where users can enter their Twitter handle; we run a query to Twitter's API and use their 200 most recent tweets to predict their location. 

Right now, the best way for you to interact with this project is to view the live website:

You are more than welcome to fork the project and start playing with it, but this will require some setup. You'll have to setup a twitter dev account to get access to the twitter stream and the twitter queries. Then you'll have to create a database to store the tweets you pull down from twitter.

The main limitation of thi project are the artificial limitations imposed by twitter involving how many queries a developer is allowed to make.
