import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import os

# ========== إعداد التوكن من متغير البيئة ==========
TOKEN = "MTM5NzIyMjM4MDMyMTExMjEzNA.GxPB6t.gsu3q37Nuoaic6c5ZdFx1PZqJ_q2JajCIGLk-k"
TARGET_CHANNEL_ID = 1396550419437719602  # ID قناة استقبال الوظائف
PING_CHANNEL_ID = 1396550419437719602    # ID القناة اللي هيبعت فيها Ping كل 5 دقائق

# ========== إعداد Discord ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========== أزرار الإدارة لقبول/رفض ==========
class AdminActions(View):
    def __init__(self, applicant: discord.User):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="✅ قبول", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            f"✅ تم قبول طلب {self.applicant.mention} من قبل {interaction.user.mention}",
            ephemeral=False
        )
        try:
            await self.applicant.send("✅ تهانينا! تم قبول طلبك للوظيفة من قبل الإدارة.")
        except:
            await interaction.followup.send("⚠️ لم أتمكن من إرسال DM للمتقدم.", ephemeral=True)
        self.disable_all_items()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ رفض", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❓ اكتب سبب الرفض:", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            reason_msg = await bot.wait_for("message", check=check, timeout=60)
            reason = reason_msg.content
        except:
            reason = "لم يتم ذكر سبب."

        await interaction.followup.send(
            f"❌ تم رفض طلب {self.applicant.mention} من قبل {interaction.user.mention}\n📝 السبب: {reason}"
        )
        try:
            await self.applicant.send(f"❌ نأسف! تم رفض طلبك.\n📝 السبب: {reason}")
        except:
            await interaction.followup.send("⚠️ لم أتمكن من إرسال DM للمتقدم.", ephemeral=True)

        self.disable_all_items()
        await interaction.message.edit(view=self)

# ========== زر فتح طلب وظيفة ==========
class JobButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 فتح طلب وظيفة", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "✅ سأجمع بياناتك الآن في الرسائل الخاصة (DM).",
            ephemeral=True
        )

        def check_dm(msg):
            return msg.author == interaction.user and isinstance(msg.channel, discord.DMChannel)

        try:
            await interaction.user.send("👋 مرحبًا! لنملأ بيانات الوظيفة.\n📝 ما اسمك داخل اللعبة؟")
            name_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            name = name_msg.content

            await interaction.user.send("💼 ما الوظيفة التي تريدها؟")
            job_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            job = job_msg.content

            await interaction.user.send("📦 ما عدد الـ Tier المطلوب؟")
            tier_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            tier = tier_msg.content

            await interaction.user.send("⏳ كم من الوقت تستطيع العمل يوميًا؟")
            time_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            time = time_msg.content

            # إرسال الطلب للإدارة
            channel = bot.get_channel(TARGET_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="📋 طلب وظيفة جديد",
                    color=discord.Color.blue()
                )
                embed.add_field(name="👤 الاسم", value=name, inline=False)
                embed.add_field(name="💼 الوظيفة", value=job, inline=False)
                embed.add_field(name="📦 التير", value=tier, inline=False)
                embed.add_field(name="⏳ الوقت المتاح", value=time, inline=False)
                embed.add_field(name="✅ مقدم الطلب", value=interaction.user.mention, inline=False)

                view = AdminActions(interaction.user)
                await channel.send(embed=embed, view=view)

                await interaction.user.send("✅ تم إرسال طلبك للإدارة. شكرًا!")
            else:
                await interaction.user.send("❌ لم أجد قناة استقبال الوظائف!")

        except Exception:
            await interaction.user.send("❌ انتهى الوقت أو حدث خطأ. حاول مرة أخرى.")

# ========== أمر إرسال زر الوظيفة ==========
@bot.command()
async def وظيفة(ctx):
    view = JobButton()
    await ctx.send("📋 اضغط على الزر أدناه لفتح طلب وظيفة:", view=view)

# ========== Loop يعمل Ping كل 5 دقائق ==========
@tasks.loop(minutes=5)
async def ping_loop():
    channel = bot.get_channel(PING_CHANNEL_ID)
    if channel:
        await channel.send("✅ Ping! البوت شغال ✅")

# ========== تشغيل البوت ==========
@bot.event
async def on_ready():
    print(f"✅ البوت شغال باسم {bot.user}")
    ping_loop.start()

bot.run(TOKEN)
