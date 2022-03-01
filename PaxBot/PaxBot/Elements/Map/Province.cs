using Discord;
using PaxBot.Elements.Units;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;

namespace PaxBot.Map
{
    public class Province
    {
        public int PID; // Province ID
        public int[] RGB = new int[3]; // nie możesz użyć typu Color bo XML nie chce go eksportować
        public List<int> Neighbours = new List<int>();
        public List<int[]> pixels = new List<int[]>();

        public List<string> Buildings = new List<string>();     // list of buildings in the province
        public List<int> Units = new List<int>();               // list of UIDs of units in the province
        public int Type;        // 0 - impassable, 1 - land, 2 - sea
        public int Level;       // development level of the province
        public string terrain;  // terrain in the province, may be used by battlemap generator
        public string Owner;    // owner User ID

        public Province()
        {
            PID = 0;
            Type = 0;
            RGB[0] = 255;
            RGB[1] = 255;
            RGB[2] = 255;
            terrain = "plains";
        } // paremeterless constructor, needed by serializer/deserializer

        public Province(int pid, System.Drawing.Color color)
        {
            terrain = "plains";
            PID = pid;
            Type = 1;
            RGB[0] = color.R;
            RGB[1] = color.G;
            RGB[2] = color.B;
        }  // constructor with paremeters, used by province generator

        public void transferProvince(string player)
        {
            Owner = player;
        } // used to easily transfer the province, will user Economizer commands to transfer the buildings

        public EmbedBuilder printProvince()
        {
            StringBuilder stringBuilder = new StringBuilder();
            stringBuilder.AppendLine("`Neighbours PID:`");
            foreach (int neighbour in Neighbours)
            {
                stringBuilder.AppendLine($"{neighbour}");
            }
            string nbrs = stringBuilder.ToString();

            var embed = new EmbedBuilder
            {
                // Embed property can be set within object initializer
                Title = $"Province {PID}",
                Color = Discord.Color.Blue
            };
            // Or with methods
            embed.AddField($"Province {PID}",
                $"`PID:`\t{PID}\n" +
                $"`Tpe:`\t{Type}\n" +
                $"`Trn:`\t{terrain}\n" +
                $"`RGB:`\t({RGB[0]},{RGB[1]},{RGB[2]})\n" +
                $"{nbrs}");

            return embed;
            /*foreach (int[] pixel in pixels)
            {
                Console.WriteLine($"Pixel:\tx = {pixel[0]}, y = {pixel[1]}");
            }*/
        } // creates a ready-to-build embed with information about the province

        public void clearPixel()
        {
            pixels.Clear();
        } // used by province generator to clean up the object

        private void export()
        {
            /*
             * Check if the user folder exists and defines the directory for further use
             */
            var path = $"D:\\PMAres\\Unit\\templates";
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);

            XmlSerializer serializer = new XmlSerializer(this.GetType()); // create serializer instance
            FileStream file; // declare FileStream for serialization
            serializer.Serialize(file = File.Create($"{path}\\{PID}.xml"), this); // serialize the object
            file.Close(); //close the file
        }
    }
}
