import discord
from discord.ext import commands
from discord import app_commands

# py files
import gcp_translate # translating in google translation api
import logger # used to write logs to google log explorer as well as to stdout
import gcp_secrets # used to get secrets from google secret manager

class Translate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''
    /TRANSLATE
    Given input text and target language, translate text from the google translation API
    '''
    @app_commands.command(name="translate", description="Translate input text to a specific language. Replies with english / translated language.")
    @app_commands.describe(text="Text to translate")
    @app_commands.choices(target_language=[
        app_commands.Choice(name="Arabic", value="ar"),
        app_commands.Choice(name="Bosnian", value="bs"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Finnish", value="fi"),
        app_commands.Choice(name="Italian", value="it"),
        app_commands.Choice(name="Portuguese", value="pt"),
        app_commands.Choice(name="Romanian", value="ro"),
        app_commands.Choice(name="Russian", value="ru"),
        app_commands.Choice(name="Serbian", value="sr"),
        app_commands.Choice(name="Spanish", value="es"),
        app_commands.Choice(name="Turkish", value="tr"),
        app_commands.Choice(name="Ukranian", value="uk")
        ])
    
    async def translate(self, interaction: discord.Interaction, text: str, target_language: app_commands.Choice[str]):
        logger.write_log(
            action='/translate',
            payload=f'User {interaction.user.name} invoked the /translate command',
            severity='Debug'
        )
        # message can take longer than 3 second timeout. defer
        await interaction.response.defer()
    
        try:
            translateDict = gcp_translate.translate_text(text, target_language.value)
            '''
            Format:
            EN: [English text]
            TR: [Translated Language]
            '''
            # if detected language is english
            if translateDict['detectedSourceLanguageISO639'] == 'en':
                await interaction.followup.send(f"English: {text}\n{target_language.name}: {translateDict['translatedText']}")
            elif target_language.value == 'en':
                await interaction.followup.send(f"English: {translateDict['translatedText']}\n{translateDict['detectedSourceLanguage']}: {text}")
            else:
                await interaction.followup.send(f"{translateDict['detectedSourceLanguage']}: {text}\n{target_language.name}: {translateDict['translatedText']}")

        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)


    '''
    /TRANSLATETHIS
    Given input text and target language, translate text from the google translation API
    '''
    @app_commands.command(name="translate_this", description="Translate input text to a specific language. Send the translation in a private message.")
    @app_commands.describe(text="Text to translate")
    @app_commands.choices(target_language=[
            app_commands.Choice(name="Arabic", value="ar"),
            app_commands.Choice(name="Bosnian", value="bs"),
            app_commands.Choice(name="Croatian", value="hr"),
            app_commands.Choice(name="English", value="en"),
            app_commands.Choice(name="German", value="de"),
            app_commands.Choice(name="Finnish", value="fi"),
            app_commands.Choice(name="Italian", value="it"),
            app_commands.Choice(name="Japanese", value="ja"),
            app_commands.Choice(name="Korean", value="ko"),
            app_commands.Choice(name="Lithuanian", value="lt"),
            app_commands.Choice(name="Macedonian", value="mk"),
            app_commands.Choice(name="Polish", value="pl"),
            app_commands.Choice(name="Portuguese", value="pt"),
            app_commands.Choice(name="Romanian", value="ro"),
            app_commands.Choice(name="Russian", value="ru"),
            app_commands.Choice(name="Serbian", value="sr"),
            app_commands.Choice(name="Slovenian", value="sl"),
            app_commands.Choice(name="Spanish", value="es"),
            app_commands.Choice(name="Swedish", value="sv"),
            app_commands.Choice(name="Turkish", value="tr"),
            app_commands.Choice(name="Ukranian", value="uk")
            ])
    async def translate_this(self, interaction: discord.Interaction, text: str, target_language: app_commands.Choice[str]):
        logger.write_log(
            action='/translate_this',
            payload=f'User {interaction.user.name} invoked the /translate command',
            severity='Debug'
        )
        # message can take longer than 3 second timeout. defer for 5 seconds
        await interaction.response.defer(ephemeral=True)
        # await asyncio.sleep(4) # Doing stuff

        try:
            translateDict = gcp_translate.translate_text(text, target_language.value)

            await interaction.followup.send(f"Detected Language: {translateDict['detectedSourceLanguage']}\n{target_language.name}: {translateDict['translatedText']}", ephemeral=True)

        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /translate_this; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)    


async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))