import discord
import os
import random
import requests
import io
from PIL import Image, ImageDraw
import gpt_2_simple as gpt2
import tarfile
import gdown
import sys


url = 'https://drive.google.com/uc?id=1EVvLwJA1f507iF1fteBOZaJUK6CbBvl-'
output = 'checkpoint_run1.tar'
gdown.download(url, output, quiet=False)
files = os.listdir()
print(files)


file_path = 'checkpoint_run1.tar'


with tarfile.open(file_path, 'r') as tar:
    tar.extractall()
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name='run1')

print('ALL DONE')

apiKey = os.environ.get('apiKey')
token = os.environ.get('token')


class MyClient(discord.Client):
    global apiKey

    async def on_ready(self):
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Astronaut In The Ocean"))
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    possibleIntros = ['Hi, My name is Shuttle. Hope I can get some space here', "Hello, I'm Shuttle! I am tasked to orbit this server",
                      "Hey, My name is Shuttle. My sensors are telling me that you might be a star", "Hello, I am Shuttle. You seem to radiate some good vibes"]

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        chan = message.channel


        if message.content.startswith('>hello'):
            await message.reply(random.choice(self.possibleIntros), mention_author=True)


        if message.content.startswith('>mars'):
            arr = []
            while arr == []:
                num = random.randint(1, 3250)
                response = requests.get(
                    'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={}&camera=navcam&api_key={}'.format(str(num), apiKey))
                if response.status_code == 200:
                    vals = response.json()
                    arr = vals['photos']
                    if len(arr) > 0:
                        photo = random.choice(arr)
                        await chan.send("Here's a picture from the red planet near us")
                        await chan.send(photo['img_src'])


        if message.content.startswith('>apod'):
            
            response = requests.get(
                'https://api.nasa.gov/planetary/apod?api_key={}'.format(apiKey))
            if response.status_code == 200:
                vals = response.json()
                await chan.send("Today's Title is: " + vals['title'])
                await chan.send(vals['url'])


        if message.content.startswith('>plot'):
            await chan.send('Contacting the nearest satellite for a new movie plot <:peepobigbrain:863049707361665024>')
            text = gpt2.generate(sess, run_name='run1',
             length=50,
             prefix="<|startoftext|>",
             truncate="<|endoftext|>\n",
             include_prefix=False,return_as_list = True)
            print(text[0])
            await chan.send(text[0])

        if message.content.startswith('>earth'):
            if len(message.mentions) == 0:
                person = message.author
            else:
                person = message.mentions[0]


            response = requests.get(person.avatar_url)
            image_bytes = io.BytesIO(response.content)
            im2 = Image.open(image_bytes)
            response = requests.get(
                'https://cdn.mos.cms.futurecdn.net/3upZx2gxxLpW7MBbnKYQLH-1200-80.jpg')
            image_bytes = io.BytesIO(response.content)
            im1 = Image.open(image_bytes)
            im2 = im2.resize((470, 470))
            mask_im = Image.new("L", im2.size, 0)
            draw = ImageDraw.Draw(mask_im)
            draw.ellipse((0, 0, im2.width, im2.height), fill=150 )
            im = im1.copy()
            im.paste(im2, (35, 40), mask_im)

            msgs = ["Zuckerberg told me that you were blue today, well, you are now the Blue Planet! <:deadinside:762920553941303327>",
                    "You are now a 12,000 km wide ball called Earth. Congratulations <:poggies:886538902184292393>",
                    "I present to you the face of the planet with 7.8 billion people who contributed nothing to the space <:superAngry:843088789349335050>"]

            with io.BytesIO() as image_binary:
                im.save(image_binary, 'PNG')
                image_binary.seek(0)
                picture = discord.File(image_binary, "space.png")
                await chan.send(random.choice(msgs))
                await chan.send(file=picture)

        if message.content.startswith('>help'):
            commands = ["1. hello : Know the bot",
                        "2. apod : Astronomical Picture Of The Day",
                        "3. mars : NAVCAM picture from planet Mars", 
                        "4. earth: Become the planet Earth, a 6 septillion kg blue ball",
                        "5. plot : DM the nearest satellite for a new movie plot"]
            msg = "Hey, heard a SOS! Here's all you need to know: \n Prefix : > \n"
            for val in commands:
                msg += val + '\n'
            await message.reply(msg)


client = MyClient()
client.run(token)
