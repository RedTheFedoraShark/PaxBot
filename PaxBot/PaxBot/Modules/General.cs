using Discord;
using Discord.Commands;
using Discord.WebSocket;
using Microsoft.Extensions.Configuration;
using System;
using System.IO;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Xml.Serialization;
using PaxBot.Map;
using static PaxBot.Various.RedUtility;
using PaxBot.Elements.Units;

namespace PaxBot.Modules
{
    public class General : ModuleBase<SocketCommandContext>
    {
        private readonly IConfiguration configuration;
        public General(IConfiguration configuration) { this.configuration = configuration; }


        [Command("Ping")] // pong!
        public async Task Pong()
        {
            /*
             * Test if bot is listening
             */
            var test = new Emoji("\U00002764");
            await Context.Message.AddReactionAsync(test);
            await ReplyAsync("Pong!");
        }

        [Command("Echo")] // echo
        public async Task Echo([Remainder] string text = null)
        {
            /*
             * Echo user's message
             */
            if (text == null) await ReplyAsync("Default message.");
            else await ReplyAsync($"{text}");
        }

        [Command("Suicide")] // kills bot process
        public async Task Suicide(SocketUser user = null)
        {
            /*
             * Owner command, kills bot process
             */
            if (user == null) user = Context.User;
            if (user.Id != Convert.ToUInt64(this.configuration["Owner"])) { await ReplyAsync("Spierdalaj"); return; }
            else await ReplyAsync("Shutting down...");
            Process.GetCurrentProcess().Kill();
        }

        [Command("List")] // list something. If admin can use list all
        public async Task List([Remainder] string text = null)
        {
            if (text == null) { await ReplyAsync("Invalid number of arguments. Argument 1 can not be NULL."); return; }
            text = text.Trim();
            text = text.ToLower();
            switch(text)
            {
                case "templates":
                    
                    break;
                default:
                    await ReplyAsync($"Invalid argument \"{text}\"");
                    break;
            }
        }

        [Command("Show")] // To do. Add a try-catch statement for checking if file is being used. Otherwise it will probably break frequently
        public async Task Show([Remainder] string text = null)
        {
            /*
             *  1. Get command parameter and test if it's valid
             *  2. Load province into memory
             *  3. Print info
             *  4. Cleanup
             *  
             * 
             */
            /*
             * Check whether there is an argument and splits arguments
             */
            if (text == null) { await ReplyAsync("Invalid number of arguments. Argument 1 can not be NULL."); return; }
            text = text.Trim();
            text = text.ToLower();
            string[] Args = text.Split(" ", 2);
            for (int i = 0; i < Args.Length; i++)
            {
                Args[i] = Args[i].Trim();
                if (Args[i] == "") { await ReplyAsync($"Invalid argument {i + 1}! Argument empty."); return; }
            }
            var path = "";
            XmlSerializer deserializer;
            FileStream file;
            EmbedBuilder embed;
            switch (Args[0])
            {
                case "army":
                    await ReplyAsync("Under construction");
                    break;
                case "unit":
                    await ReplyAsync("Under construction.");
                    break;
                case "template":
                    path = "D:\\PMAres\\Unit\\templates"; // path to provinces folder
                    /* Check if the argument is correct */
                    if (Args.Length!=2) { await ReplyAsync($"Template name unspecified!"); return; }
                    if (!FileExistsRecursive(path,$"{Args[1]}.xml", out path)) { await ReplyAsync($"Template name invalid! There is no template named {Args[1]}"); return; }
                    BattleStats template = new BattleStats();
                    deserializer = new XmlSerializer(template.GetType());
                    file = new FileStream($"{path}\\{Args[1]}.xml", FileMode.Open);
                    template = (BattleStats)deserializer.Deserialize(file);
                    file.Close();
                    embed = template.printStats();
                    await ReplyAsync(embed: embed.Build());
                    // cleanup
                    template = null;
                    embed = null;
                    break;

                case "province":
                    int pid = Convert.ToInt32(Args[1]);
                    path = "D:\\PMAres\\provinces"; // path to provinces folder
                    /* Check if the argument is correct */
                    if (pid < 0 || pid >= GetDirectoryFileCount(path)) { await ReplyAsync($"Province PID invalid! There is no province with ID {Args[1]}"); return; }
                    Province province = new Province();
                    deserializer = new XmlSerializer(province.GetType());
                    file = new FileStream($"{path}\\{pid}.xml", FileMode.Open);
                    province = (Province)deserializer.Deserialize(file);
                    file.Close();
                    embed = province.printProvince();
                    await ReplyAsync(embed: embed.Build());
                    // cleanup
                    province = null;
                    break;

                 default:
                    await ReplyAsync($"Invalid argument \"{Args[0]}\"");
                    break;

            }
        }

        [Command("Create")] // used to create different objects
        [Alias("Create,")]  // fix arguments later so there doesn't have to be a ',' after argument[0]
        public async Task Create([Remainder] string text = null)
        {
            /*
             * Check whether there is an argument and splits arguments
             */
            if (text == null) { await ReplyAsync("Invalid number of arguments. Argument 1 can not be NULL."); return; }
            text = text.Trim();
            text = text.ToLower();
            string[] Args = text.Split(",");
            for (int i = 0; i < Args.Length; i++)
            {
                Args[i] = Args[i].Trim();
                if (Args[i] == "") { await ReplyAsync($"Invalid argument {i + 1}! Argument empty."); return; }
            }
            switch (Args[0])
            {


                case "template":
                    /* Check for right number of arguments */
                    if (Args.Length != 13) { await ReplyAsync("Invalid number of arguments!"); return; }
                    /* Check if the int arguments are actually correct */
                    for (int i = 3; i < 12; i++) { if (Convert.ToInt32(Args[i]) > 6 || Convert.ToInt32(Args[i]) < 0) { await ReplyAsync($"Invalid argument {i + 1}! Argument out of range. Argument must be: 0<x<6."); return; } }
                    /* Check if the mention user is actually correct */
                    ulong number;
                    if (!MentionUtils.TryParseUser(Args[12], out number)) {await ReplyAsync($"Can't parse \"{Args[12]}\"! User does not exist or is not correct."); return; }
                    BattleStats bs = new BattleStats(Args[1], Convert.ToInt32(Args[2]), Convert.ToInt32(Args[3]), Convert.ToInt32(Args[4]), Convert.ToInt32(Args[5]), Convert.ToInt32(Args[6]), Convert.ToInt32(Args[7]), Convert.ToInt32(Args[8]), Convert.ToInt32(Args[9]), Convert.ToInt32(Args[10]), Convert.ToInt32(Args[11]), Args[12]);
                    await ReplyAsync("Created?");
                    break;
                default:
                    await ReplyAsync($"Invalid argument \"{Args[0]}\"");
                    break;
            }
        }

        [Command("Help")] // help
        public async Task Help()
        {
            var embed = new EmbedBuilder
            {
                // initializer with basic embed info
                Title = "Command List",
                Description = "This is a command list",
                Color = Color.Orange
            };
            // methods with command info
            embed.AddField
                ("help",
                "Prints this help embed.");
            embed.AddField
                ("ping", 
                "If the bot is working, he should reply \"Pong!\".");
            embed.AddField
                ("Show",
                "Prints info about specified object.");
            embed.AddField
                ("echo [text]",
                "If the bot is working, he should reply \"[text]\".");

            //Your embed needs to be built before it is able to be sent
            await ReplyAsync(embed: embed.Build());
        }


    }
}
