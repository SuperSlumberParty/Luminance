from discord import Webhook, Embed, Color
import configparser
import aiohttp, asyncio
import re
import subprocess
from watchfiles import awatch

class Radiance:

    def __init__(self):
        self.rgx = "-\s(.*?)\s\[(.*?)]\s\"(.*?)\s\/(.*?).HTTP"
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini')
        self.lastevent = []
        asyncio.run(self.watch(self.config['GITEA']['AccessLog']))

    async def regexCascade(self, query):
        # Returns Username, Date, Type and broken down url
        firstrgxres = re.findall(self.rgx, query)
        if firstrgxres == []:
            return None
        urlsplit = firstrgxres[0][3].split("/")
        return [firstrgxres[0][0], firstrgxres[0][1].split(" ")[0], urlsplit]


    async def process(self, logentry):
        parsed = await self.regexCascade(logentry)
        self.action = ""
        if parsed == None:
            return
        if " 200 " in logentry:
            if 'git-receive-pack' in logentry:
                self.action = "push"
            elif 'git-upload-pack' in logentry:
                self.action = "pull"
            elif '/archive/' in logentry:
                self.action = "archive download"

            if self.action != "":
                if self.lastevent != [parsed[0], self.action, f'{parsed[2][0]}/{parsed[2][1]}']:
                    self.lastevent = [parsed[0], self.action, f'{parsed[2][0]}/{parsed[2][1]}']
                    await self.sendWebhook(parsed, self.action)
                else:
                    print("Duplicate, skipped")
    
    async def createEmbed(self, action, parsed):
            e = Embed(title="Luminance", description=f"New {self.action}", color=Color.from_rgb(255, 188, 188))
            e.add_field(name="User", value=f"{parsed[0]}")
            e.add_field(name="Repository", value=f"{self.config['GITEA']['URL']}{parsed[2][0]}/{parsed[2][1]}")
            return e

    async def sendWebhook(self, parsed, action):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.config['DISCORD']['WebhookURL'], session=session)

            if self.config.has_option("REPOSITORY", 'UserOrg') or self.config.has_option("REPOSITORY", 'RepositoryName'):
                if self.config.getboolean("REPOSITORY", 'RelativeURL') == True:
                    if f'{parsed[2][0]}/{parsed[2][1]}' == f'{self.config["REPOSITORY"]["UserOrg"]}/{self.config["REPOSITORY"]["RepositoryName"]}':
                        embed = await self.createEmbed(action, parsed)
                else:
                    if self.config.has_option("REPOSITORY", 'UserOrg'):
                        if f'{parsed[2][0]}' == f'{self.config["REPOSITORY"]["UserOrg"]}':
                            embed = await self.createEmbed(action, parsed)
                    elif self.config.has_option("REPOSITORY", 'RepositoryName'):
                        if f'{parsed[2][1]}' == f'{self.config["REPOSITORY"]["RepositoryName"]}':
                            embed = await self.createEmbed(action, parsed)

            else:
                embed = await self.createEmbed(action, parsed)
            
            try:
                await webhook.send(embed=embed) 
            except UnboundLocalError:
                pass

    async def watch(self, filename):
        async for changes in awatch(filename):
            out = subprocess.check_output(['tail', '-1', filename])[0:-1].decode()
            await self.process(out)

if __name__ == "__main__":
    radiance = Radiance()
