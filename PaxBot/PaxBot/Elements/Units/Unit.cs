using Discord;
using Discord.WebSocket;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;
using static PaxBot.Various.RedUtility;

namespace PaxBot.Elements.Units
{
    public class Unit
    {
        string Name;            // Unit Name, can be customized
        int UID;                // Unit ID
        string Owner;    // Unit owner ID
        BattleStats Statistics; // Battle Statistics
        uint 
            MaxCapmMovement,    // Max Campaign movement
            CampMovement;       // Campaign Movement, regenerates every turn
        int Position;           // PID of the province unit is in
        int AID = -1;                // Army ID the unit belongs to. Can be ytpme (-1).

        Unit(SocketUser user)
        {
        } // default constructor, needed for serialization/deserialization and tests

        Unit(int pos, BattleStats stats, uint movement, string user)
        {
            user = Convert.ToString(MentionUtils.ParseUser(user));
            Owner = user;
            UID = GetDirectoryFileCountRecursive($"D:\\PMAres\\Unit\\units");
            Position = pos;
            MaxCapmMovement = movement;
            CampMovement = 0;
        }

        private void export(string user) // local function for exporting the template
        {
            /*
             * Check if the user folder exists and defines the directory for further use
             */
            var path = $"D:\\PMAres\\Unit\\units\\{user}";
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);

            XmlSerializer serializer = new XmlSerializer(this.GetType()); // create serializer instance
            FileStream file; // declare FileStream for serialization
            serializer.Serialize(file = File.Create($"{path}\\{UID}.xml"), this); // serialize the object
            file.Close(); //close the file

        }

        public EmbedBuilder printUnit()
        {
            var embed = new EmbedBuilder
            {
                // Embed property can be set within object initializer
                Title = $"Unit {Name}",
                Color = Discord.Color.Green
            };
            // Or with methods
            embed.AddField("Campaign Info",
                $"`UID:` {UID}\n" +
                $"`Pos:` {Position}\n" +
                $"`Mvt:` {CampMovement}/{MaxCapmMovement}\n" +
                $"`Own:` @{Owner}\n");
            embed.AddField("Battle Stats",
                 Statistics.printStats());
            return embed;
        }
    }

    public class BattleStats // literally unit templates
    {
        //string path = $"{Directory.GetCurrentDirectory()}\\";

        public string owner;           // owner user ID, so people can't see each others' templates
        public string templateName;    // name of the template
        public int
            MaxSize,            // Max Size of the unit
            CurrentSize,        // Curent size of the unt
            R, D, WW, US, SM, SS, SD, W, A; //Stats

        public BattleStats() // default constructor, needed for serialization/deserialization and tests
        {
            templateName = "Milicja";
            MaxSize = 100;
            CurrentSize = MaxSize;
            R = 2;
            D = 0;
            WW = 5;
            US = 7;
            SM = 2;
            SS = 0;
            SD = 0;
            W = 2;
            A = 1;
        }

        public BattleStats(string name, int size, int r, int d, int ww, int us, int sm, int ss, int sd, int w, int a, string user)
        {
            user = Convert.ToString(MentionUtils.ParseUser(user));
            owner = user;
            templateName = name;
            MaxSize = size;
            CurrentSize = size;
            R = r;
            D = d;
            WW = ww;
            US = us;
            SM = sm;
            SS = ss;
            SD = sd;
            W = w;
            A = a;
            export(user);
        } // proper template constructor

        private void export(string user) // local function for exporting the template
        {
            /*
             * Check if the user folder exists and defines the directory for further use
             */
            var path = $"D:\\PMAres\\Unit\\templates\\{user}";
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);
            
            XmlSerializer serializer = new XmlSerializer(this.GetType()); // create serializer instance
            FileStream file; // declare FileStream for serialization
            serializer.Serialize(file = File.Create($"{path}\\{templateName}.xml"), this); // serialize the object
            file.Close(); //close the file
            
        }

        public string returnName()
        {
            return templateName;
        }

        public string returnStats() // used for printing. Builds and returns a string to be used in an embed 
        {
            StringBuilder stringBuilder = new StringBuilder();
            stringBuilder.AppendLine($"`Size:`{CurrentSize}/{MaxSize}");
            stringBuilder.AppendLine($"`R :` {R}");
            stringBuilder.AppendLine($"`D :` {D}");
            stringBuilder.AppendLine($"`WW:` {WW}");
            stringBuilder.AppendLine($"`US:` {US}");
            stringBuilder.AppendLine($"`S :` {SM}M {SS}S {SD}D");
            stringBuilder.AppendLine($"`W :` {W}");
            stringBuilder.AppendLine($"`A :` {A}");
            return stringBuilder.ToString();
        }

        public EmbedBuilder printStats() // used for printing. Builds and returns an embedbuilder ready to build
        {
            var embed = new EmbedBuilder
            {
                // Embed property can be set within object initializer
                Title = $"Template {templateName}",
                Color = Discord.Color.Blue
            };
            // Or with methods
            embed.AddField($"Template {templateName}", returnStats());
            return embed;
        }

        public void changeStat(string[] args) // used for changing stat values. Uses arrays for changing multiple stats at once
        {
            for (int i = 0; i < args.Length; i++)
            {
                string[] stat = args[i].Split(':', 2);
                switch (stat[0])
                {
                    case "R":
                        R = Convert.ToInt32(stat[1]);
                        break;
                    case "D":
                        D = Convert.ToInt32(stat[1]);
                        break;
                    case "WW":
                        WW = Convert.ToInt32(stat[1]);
                        break;
                    case "US":
                        US = Convert.ToInt32(stat[1]);
                        break;
                    case "SM":
                        SM = Convert.ToInt32(stat[1]);
                        break;
                    case "SSZ":
                        SS = Convert.ToInt32(stat[1]);
                        break;
                    case "SD":
                        SD = Convert.ToInt32(stat[1]);
                        break;
                    case "W":
                        W = Convert.ToInt32(stat[1]);
                        break;
                    case "A":
                        A = Convert.ToInt32(stat[1]);
                        break;
                    default:
                        break;
                }
            }
        }
 
    }
}
