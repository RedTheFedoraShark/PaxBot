using Discord.Commands;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PaxBot.Modules
{
    public class Battle : ModuleBase<SocketCommandContext>
    {
        [Command("battle")]
        public async Task battle([Remainder] string args)
        {
            string[] Arguments = args.Split(",");
            foreach (string argument in Arguments) argument.Trim();

            await ReplyAsync("PaxbBot.Modules.Battle");
        }
    }
}
