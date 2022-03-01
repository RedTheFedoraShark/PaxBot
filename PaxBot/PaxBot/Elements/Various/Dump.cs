using PaxBot.Map;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;
using static PaxBot.Various.RedUtility;


namespace PaxBot.Various
{
    class Dump
    {
        /*
         * Dump for any code (or parts of it) I may or may not need in the future
         */



        static private void export (List<Province> provinces, bool truncate)
        {
            printPMA("Exporting...");
            XmlSerializer serializer = new XmlSerializer(provinces[0].GetType()); // create serializer instance
            FileStream file; // declare FileStream for serialization
            foreach(Province province in provinces)
            {
                if(truncate) province.clearPixel(); // clear pixel array
                serializer.Serialize(file = File.Create($"D:\\PMAres\\provinces\\{province.PID}.xml"), province); // serialize the object
                file.Close(); //close the file
            }
            printPMA("Exportning done.");
        }
        static private void import(List<Province> provinces)
        {
            printPMA("Importing...");
            var path = "D:\\PMAres\\provinces"; // path to provinces folder
            int fileCount = GetDirectoryFileCount(path);
            printSystem($"{fileCount}");
            XmlSerializer deserializer = new XmlSerializer(test.GetType());
            for (int i = 0; i < fileCount; i++)
            {
                FileStream file = new FileStream($"{path}\\{i}.xml", FileMode.Open);
                provinces.Add((Province)deserializer.Deserialize(file));
            }
            printPMA("Importing done.");

        }
    }
}
