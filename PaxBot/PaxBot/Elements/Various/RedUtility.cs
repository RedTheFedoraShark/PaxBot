using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PaxBot.Various
{
    class RedUtility
    {
        public static void printSystem(string s)
        {
            Console.WriteLine($"System:\t{s}");
        }

        public static void printError(string s)
        {
            Console.WriteLine($"Error:\t{s}");
        }

        public static void printPMA(string s)
        {
            Console.WriteLine($"PMA:\t{s}");
        }

        /*
         * Gets count of all files in specified directory.
         * Not Recursive
         */
        public static int GetDirectoryFileCount(string dir)
        {
            int fileCount = 0;
            dir = dir + @"\";
            //get all the directories and files inside a directory
            String[] all_files = Directory.GetFileSystemEntries(dir);
            //loop through all items
            foreach (string file in all_files)
            {
                //check to see if the file is a directory if not increment the count
                if (!Directory.Exists(file))
                {
                    fileCount++;
                }
            }

            return fileCount;
        }

        public static int GetDirectoryFileCountRecursive(string dir)
        {
            int fileCount = 0;
            dir = dir + @"\";
            //get all the directories and files inside a directory
            String[] all_files = Directory.GetFileSystemEntries(dir);
            //loop through all items
            foreach (string file in all_files)
            {
                //check to see if the file is a directory if not increment the count
                if (!Directory.Exists(file))
                {
                    fileCount++;
                }
                else GetDirectoryFileCountRecursive(file);
            }

            return fileCount;
        }

        public static bool FileExistsRecursive(string rootPath, string filename, out string path )
        {
            if (File.Exists(Path.Combine(rootPath, filename)))
            { path = rootPath; return true; }
              

            foreach (string subDir in Directory.GetDirectories(rootPath))
            {
                if (FileExistsRecursive(subDir, filename, out path))
                { path = subDir; return true; }
            }
            path = null;
            return false;
        }







        /*public virtual bool IsFileLocked(FileInfo file)
        {
            try
            {
                using (FileStream stream = file.Open(FileMode.Open, FileAccess.Read, FileShare.None))
                {
                    stream.Close();
                }
            }
            catch (IOException)
            {
                //the file is unavailable because it is:
                //still being written to
                //or being processed by another thread
                //or does not exist (has already been processed)
                return true;
            }

            //file is not locked
            return false;
        }*/
    }
}
