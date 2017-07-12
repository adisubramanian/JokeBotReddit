import praw
import sys
import os
import requests
import json
import time
import numpy as np
import random

PATH = r"""C:\Users\Aditya\Desktop\CodeProjects\JokeBotLogin\login.txt"""

#This is a reddit bot that attempts to get karma from reposts
#It does this by finding similar posts,
#If there are popular similar posts, it will copy the top response
#and respond to the new post with that response
#this is particularly meant to be used on r/jokes
#but could potentially be used on a variety of other subreddits
def getLoginInfo():
	#I don't want to reveal my password so its in a different folder
	#To use this yourself change path
	#and update the username, pass, clientid, and client secret
	f = open(PATH, "r")
	lines = f.readlines()
	f.close()
	'''
	username = lines[0].strip()
	password = lines[1].strip()
	client_id = lines[2].strip()
	client_secret = lines[3].strip()'''
	return [l.strip() for l in lines]

def runBot():
	f = open("commentsWritten.txt", "w")
	info = getTopN("jokes", 1000)
	bot = info[4]
	subreddit = bot.subreddit("jokes")
	print("got data")


	for sub in subreddit.stream.submissions():
		postTitle = sub.title
		print(postTitle)
		postContent = sub.selftext
		combined = postTitle + " " + postContent
		for i in range(len(info[0])):
			go = False
			if levenshtein(postTitle, info[0][i]) < ((len(postTitle)/20) + 1):
				go = True
			elif levenshtein(combined, info[2][i]) < ((len(combined)/20) + 1):
				go = True
			if go:
				print("ayyy\n")
				time.sleep(100 + random.randint(1, 250))#It'd be weird if we posted at exactly the same time each post, right?
				try:
					comment = sub.reply(info[3][i])
				except:
					time.sleep(300)
					comment = sub.reply(info[3][i])
				f.write(sub.url)
				f.write("\n \n")
				try:
					f.write(comment.body)
				except:
					try:
						f.write(comment)
					except:
						pass
				f.write("\n")

				break
		if not go:
			print("nah\n")




def getTopN(subreddit, n):
	'''
	Takes in a subreddit name and a number of posts to look at
	'''
	#in order to see if the post is a repost, I want a "database" of top posts to compare it to
	#although since its all text its really not worth storing.


	loginInfo = getLoginInfo()
	bot = praw.Reddit(user_agent='joker',
					  client_id=loginInfo[2],
					  client_secret=loginInfo[3],
					  username=loginInfo[0],
					  password=loginInfo[1])
	subreddit = bot.subreddit("jokes")
	
	Titles = []
	Contents = []
	TitleAndContents = []
	Comments = []
	i = 0
	for sub in subreddit.top('all', limit = n):
		#sub = praw.models.Submission(bot, id = submission)
		postTitle = sub.title
		postContent = sub.selftext
		if "edit: " in postContent:
			postContent = postContent.split("edit: ")[0]
		elif "Edit" in postContent:
			postContent = postContent.split("Edit")[0]
		#print(sub.comments[0].body)
		topComment = sub.comments[0].body
		if "edit: " in topComment:
			topComment = topComment.split("edit: ")[0]
		elif "Edit" in topComment:
			topComment = topComment.split("Edit")[0]
		Titles.append(postTitle)
		Contents.append(postContent)
		TitleAndContents.append(postTitle + " " + postContent)
		Comments.append(topComment)
		print(i)
		i = i + 1
	return Titles, Contents, TitleAndContents, Comments, bot


def levenshtein(source, target):
	#shamelessly stolen from: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    #seriously its remarkably fast. No shame whatsoever.
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


runBot()