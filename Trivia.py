from discord.ext import commands
import discord
from datetime import datetime
import json
import urllib.request
import random
import html
import re

class Trivia(commands.Cog):

    CurrentQuestion = None
    AnswerOptions = ["A. ", "B. ", "C. ", "D. ", "E. ", "F. "]
    AllowedEmojis = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫"]

    class AnswerSubmission:
        User = None
        Answer = -1

        def __init__(self, User, Answer):
            self.User = User
            self.Answer = Answer

        def __eq__(self, other):
            return other.User == self.User

    # ------------------------------------------------------------------------------

    class Question:
        question = ""
        incorrectanswers = []
        answer = ""
        category = ""
        allowedreacts = []
        answerEntries = []
        messageRef = None

        _totalanswers = []
        _correctAnswer = -1

        def  __init__(self, data):
            self.question = self.SanitiseAndReplace(data['results'][0]['question'])
            self.answer = data['results'][0]['correct_answer']
            self.incorrectanswers = data['results'][0]['incorrect_answers']
            self.category = data['results'][0]['category']
            self._totalanswers = self.incorrectanswers
            self.scrambleanswers()
            self._correctAnswer = self._totalanswers.index(self.answer)

        def SanitiseAndReplace(self, text):
            return html.unescape(text)

        def SanitiseAndReplaceArray(self, array):
            for x in array:
                x = self.SanitiseAndReplace(x)
            return array

        def scrambleanswers(self):
            self._totalanswers.append(self.answer)
            random.shuffle(self._totalanswers)
            self._totalanswers = self.SanitiseAndReplaceArray(self._totalanswers)

        def GetNumAnswers(self):
            return len(self._totalanswers)

        def GetCorrectAnswer(self):
            return self._correctAnswer

    # ------------------------------------------------------------------------------

    def __init__(self, bot, config):
        self.bot = bot
        self.start_time = datetime.now()
        self.config = config
        self.CurrentQuestion = None

    def GetQuestionEmbedTemplate(self, question):
        embed = discord.Embed(title=question.question, description=question.category, color=0x2bff00)
        embed.set_thumbnail(url="https://i.pinimg.com/564x/d2/3d/37/d23d37bbb847e47055ee5299b1d69be2.jpg")

        index = 0
        for x in question._totalanswers:
            embed.add_field(name=self.AnswerOptions[index], value=str(x), inline=False)
            index+=1
        embed.set_footer(text="Type !reveal to show answer")
        return embed

    async def GetAnswerEmbedTemplate(self, question):
        embed = discord.Embed(title="The correct answer was " + question.answer, description="Results are...", color=0x2bff00)
        users = await self.AllUsersWhoReacted(question.messageRef)

        for user in users:
            icon = ""
            if await self.WasUserCorrect(user, question):
                icon = '✅'
            else:
                icon = '❌'
            embed.add_field(name=user.name, value=icon, inline=True)
        return embed

    async def WasUserCorrect(self, user, question):
        correctReact = None
        for react in question.messageRef.reactions:
            if react.emoji == question.allowedreacts[question.GetCorrectAnswer()]:
                correctReact = react
                break
        usersWhoReacted = await correctReact.users().flatten()
        return user in usersWhoReacted

    async def AllUsersWhoReacted(self, message):
        users = set()
        for reaction in message.reactions:
            async for user in reaction.users():
                users.add(user)
        users.remove(self.bot.user)
        return users

    # ------------------------------------------------------------------------------

    @commands.command()
    async def trivia(self, ctx):
        """Get a random question!"""
        url = "https://opentdb.com/api.php?amount=1"

        response = urllib.request.urlopen(url)
        data = json.loads(response.read())

        question = self.Question(data)
        weakMessage = await ctx.send(embed=self.GetQuestionEmbedTemplate(question))
        question.messageRef = discord.utils.get(self.bot.cached_messages, id=weakMessage.id)
        for i in range(question.GetNumAnswers()):
            await question.messageRef.add_reaction(self.AllowedEmojis[i])
            question.allowedreacts.append(self.AllowedEmojis[i])

        self.CurrentQuestion = question

    # ------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if self.CurrentQuestion != None:
            questionmessage = self.CurrentQuestion.messageRef
            if questionmessage != None:
                if questionmessage == reaction.message: #reaction to our question message
                    if user != self.bot.user:
                        emoji = reaction.emoji
                        if emoji not in self.CurrentQuestion.allowedreacts:
                            await reaction.remove(user)
                        else:
                            for react in questionmessage.reactions:
                                usersWhoReacted = await react.users().flatten()
                                if react != reaction and user in usersWhoReacted: #if this user has already reacted
                                    await reaction.remove(user)

    #------------------------------------------------------------------------------

    @commands.command()
    async def reveal(self, ctx):
        """Reveals the answer to the previous trivia question."""
        if self.CurrentQuestion != None:
            answerEmbed = await self.GetAnswerEmbedTemplate(self.CurrentQuestion)
            await ctx.send(embed=answerEmbed)
            self.CurrentQuestion = None

    # ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------