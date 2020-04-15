import os
import discord
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():

    # Reading in user data
    with open('Memory.txt') as json_file:
        userData = json.load(json_file)

    for guild in client.guilds:
        if guild.id == GUILD:
            break

    # Printing bot and server info
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # Printing current members of server
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    # Adding new users (if there are any)
    for member in guild.members:

        if not(member.name in userData['users']):
            # Must add them to the list
            userData['users'][member.name] = {
                'lastVideoDate': 'none',
                'currentStreak': 0,
                'longestStreak': 0
            }

    # Saving user data
    with open('Memory.txt', 'w') as outfile:
        json.dump(userData, outfile)


@client.event
async def on_message(message):

    # Reading in user data
    with open('Memory.txt') as json_file:
        userData = json.load(json_file)

    # It is possible someone new joined.
    for guild in client.guilds:
        if guild.id == GUILD:
            break

    # Adding new users (if there are any)
    for member in guild.members:

        if not (member.name in userData['users']):
            # Must add them to the list
            userData['users'][member.name] = {
                'lastVideoDate': 'none',
                'currentStreak': 0,
                'longestStreak': 0
            }

    if message.author == client.user:
        return

    attachments = message.attachments

    sendResponseString = 0

    for attachment in attachments:
        filename = str(attachment).split(' ')[2]

        if filename.find('.mp4') != -1 or filename.find('.wmv') != -1:
            userName = str(message.author).split('#')[0]
            print(userName + " has sent a video.")

            # Analyzing users data
            todaysDate = datetime.today().strftime('%Y-%m-%d')
            yesterdaysDate = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
            lastUserVideoDate = userData['users'][userName]['lastVideoDate']
            currentUserStreak = userData['users'][userName]['currentStreak']
            totalNumber = userData['users'][userName]['totalNumber']
            userData['users'][userName]['totalNumber'] = totalNumber + 1

            if lastUserVideoDate == 'none':
                userData['users'][userName]['lastVideoDate'] = todaysDate
                userData['users'][userName]['currentStreak'] = 1
                sendResponseString = 1
            elif lastUserVideoDate == yesterdaysDate:
                userData['users'][userName]['lastVideoDate'] = todaysDate
                userData['users'][userName]['currentStreak'] = currentUserStreak + 1
                sendResponseString = 1
            elif lastUserVideoDate == todaysDate:
                response = "You have already submitted a video for today."
                await message.channel.send(response)
            else:
                userData['users'][userName]['lastVideoDate'] = todaysDate
                userData['users'][userName]['currentStreak'] = 1
                sendResponseString = 1

    # Checking if users are still on their streak or not.
    for member in guild.members:
        # Analyzing users data
        userName = member.name
        todaysDate = datetime.today().strftime('%Y-%m-%d')
        yesterdaysDate = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        lastUserVideoDate = userData['users'][userName]['lastVideoDate']
        currentUserStreak = userData['users'][userName]['currentStreak']
        longestUserStreak = userData['users'][userName]['longestStreak']

        if currentUserStreak > longestUserStreak:
            userData['users'][userName]['longestStreak'] = currentUserStreak

        if lastUserVideoDate != todaysDate and lastUserVideoDate != yesterdaysDate:
            userData['users'][userName]['currentStreak'] = 0


    if sendResponseString == 1:
        userData, response = makeResponseString(userData)
        await message.channel.send(response)

    # Saving user data
    with open('Memory.txt', 'w') as outfile:
        json.dump(userData, outfile)


def makeResponseString(userData):

    response = "VIDEO STREAK RANKINGS\n===================\n"

    allUsersStreaks = []
    rankings = []

    for user in userData['users']:
        userName = str(user)
        if userName != "Streaker":
            allUsersStreaks.append(userData['users'][userName]['currentStreak'])

    allUsersStreaks.sort(reverse=True)

    newUserData = userData
    usersRanked = ['Streaker']

    for i in range(len(allUsersStreaks)):
        rank = []
        for user in newUserData['users']:
            if not(user in usersRanked):
                tempUserStreak = newUserData['users'][user]['currentStreak']
                tempUserLongestStreak = newUserData['users'][user]['longestStreak']
                tempUserTotal = newUserData['users'][user]['totalNumber']
                if tempUserStreak == allUsersStreaks[i]:
                    rank = [user, tempUserStreak, tempUserLongestStreak, tempUserTotal]
                    usersRanked.append(user)
                    break

        rankings.append(rank)

    for i in range(len(rankings)):
        response += str(i + 1) + ") " + rankings[i][0] + "\n----------------------------------------\nCurrent Streak: " + str(rankings[i][1]) + " - Longest Streak: " + str(rankings[i][2]) + " - Total: " + str(rankings[i][3]) + "\n----------------------------------------\n\n"

    response += "How high can your streak get?"

    return userData, response



client.run(TOKEN)
